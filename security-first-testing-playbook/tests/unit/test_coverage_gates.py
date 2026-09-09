"""Slides 19 and 25 — mutation score and diff coverage as the gates that matter."""

from __future__ import annotations

from stplaybook.quality.coverage import (
    MutationOutcome,
    diff_coverage,
    evaluate_gates,
    mutation_score,
)


def test_diff_coverage_counts_only_changed_lines() -> None:
    assert diff_coverage({1, 2, 3, 4, 5}, {1, 2, 3, 4}) == 80.0


def test_diff_coverage_of_a_commit_touching_nothing_is_complete() -> None:
    """A commit with no executable change cannot regress coverage."""
    assert diff_coverage(set(), {1, 2, 3}) == 100.0


def test_timeout_convention_moves_the_mutation_score_materially() -> None:
    """Slide 19's single formula hides this; the flag makes it explicit."""
    outcome = MutationOutcome(killed=68, survived=25, timed_out=4, no_coverage=10)

    counted = mutation_score(outcome, count_timeouts_as_killed=True)
    excluded = mutation_score(outcome, count_timeouts_as_killed=False)

    assert round(counted, 1) == 74.2
    assert round(excluded, 1) == 70.1


def test_uncovered_mutants_are_excluded_from_the_denominator() -> None:
    """Coverage is diff coverage's question, not the mutation score's."""
    without = mutation_score(MutationOutcome(killed=9, survived=1))
    with_uncovered = mutation_score(MutationOutcome(killed=9, survived=1, no_coverage=90))

    assert without == with_uncovered == 90.0


def test_gate_reports_every_breach_not_merely_the_first() -> None:
    """A gate revealing one problem per run trains one fix per run."""
    result = evaluate_gates(
        diff_coverage_pct=72.0,
        mutation_score_pct=61.0,
        flaky_rate_pct=3.2,
        quarantined_in_critical_band=1,
    )

    assert result.passed is False
    assert len(result.reasons) == 4


def test_gate_passes_when_every_threshold_is_met() -> None:
    result = evaluate_gates(
        diff_coverage_pct=86.0,
        mutation_score_pct=74.0,
        flaky_rate_pct=0.4,
        quarantined_in_critical_band=0,
    )

    assert result.passed is True
    assert result.reasons == []
