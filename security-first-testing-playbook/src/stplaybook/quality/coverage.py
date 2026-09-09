"""Coverage and mutation gates.

Slide 25: gate on **diff coverage** and **mutation score**; report line coverage
as context; never set an organisation-wide line-coverage target.  This module
implements only the two measures worth gating on.

**Correction to slide 19.**  The slide gives the mutation score as
``killed / (killed + survived)``.  Real tools also emit timeouts, no-coverage and
compile errors, and whether timeouts count as killed is a convention that moves
the number materially.  It is an explicit flag here.
"""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = ["GateResult", "MutationOutcome", "diff_coverage", "evaluate_gates", "mutation_score"]


@dataclass(frozen=True)
class MutationOutcome:
    """The tally a mutation run produces."""

    killed: int = 0
    survived: int = 0
    timed_out: int = 0
    no_coverage: int = 0

    @property
    def total(self) -> int:
        return self.killed + self.survived + self.timed_out + self.no_coverage


@dataclass(frozen=True)
class GateResult:
    """Whether the gates pass, and precisely why not when they do not."""

    passed: bool
    reasons: list[str] = field(default_factory=list)

    def describe(self) -> str:
        if self.passed:
            return "All quality gates passed."
        return "Quality gates failed:\n  - " + "\n  - ".join(self.reasons)


def diff_coverage(changed_lines: set[int], covered_lines: set[int]) -> float:
    """Percentage of changed lines that a test executed.

    Returns ``100.0`` when nothing changed: a commit touching no executable line
    cannot regress coverage, and failing it would train people to game the
    metric with cosmetic edits.
    """
    if not changed_lines:
        return 100.0
    return len(changed_lines & covered_lines) / len(changed_lines) * 100


def mutation_score(outcome: MutationOutcome, *, count_timeouts_as_killed: bool = True) -> float:
    """Percentage of *detected* mutants among those the suite could reach.

    ``no_coverage`` mutants are excluded from the denominator: they measure
    coverage, which diff coverage already gates.  Including them would conflate
    two questions and make the score respond to the wrong fix.
    """
    killed = outcome.killed + (outcome.timed_out if count_timeouts_as_killed else 0)
    detectable = killed + outcome.survived + (0 if count_timeouts_as_killed else outcome.timed_out)
    if detectable == 0:
        return 0.0
    return killed / detectable * 100


def evaluate_gates(
    *,
    diff_coverage_pct: float,
    mutation_score_pct: float,
    flaky_rate_pct: float,
    quarantined_in_critical_band: int,
    diff_coverage_floor: float = 80.0,
    mutation_score_floor: float = 70.0,
    flaky_rate_ceiling: float = 1.0,
) -> GateResult:
    """Apply the deck's published gates and report every breach.

    Every failure is listed rather than short-circuiting on the first, because a
    gate that reveals one problem per run trains people to fix them one per run.
    """
    reasons: list[str] = []
    if diff_coverage_pct < diff_coverage_floor:
        reasons.append(
            f"diff coverage {diff_coverage_pct:.1f}% is below the {diff_coverage_floor:.0f}% floor"
        )
    if mutation_score_pct < mutation_score_floor:
        reasons.append(
            f"mutation score {mutation_score_pct:.1f}% is below "
            f"the {mutation_score_floor:.0f}% floor"
        )
    if flaky_rate_pct > flaky_rate_ceiling:
        reasons.append(
            f"flakiness {flaky_rate_pct:.2f}% exceeds the {flaky_rate_ceiling:.2f}% ceiling"
        )
    if quarantined_in_critical_band > 0:
        reasons.append(
            f"{quarantined_in_critical_band} quarantined test(s) in the critical band; "
            "the release gate requires zero"
        )
    return GateResult(passed=not reasons, reasons=reasons)
