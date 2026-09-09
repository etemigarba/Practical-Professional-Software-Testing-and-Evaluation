"""Risk-based vulnerability triage: four signals, in order.

Slide 47's argument: patching by CVSS severity alone means patching almost
everything, which in practice means patching late.  The four signals are applied
in a fixed precedence so that the outcome is explainable, and every result
carries the reasoning that produced it.

**Correction to slide 47.**  The slide presents the P0-P3 tiers as a fixed
table.  A table cannot be recomputed when an organisation's exposure profile
differs, so the mapping is implemented here as inspectable rules with adjustable
thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

__all__ = ["CVSS_HIGH", "EPSS_HIGH", "Finding", "Tier", "TriageResult", "triage"]

EPSS_HIGH = 0.10
"""EPSS probability above which exploitation is treated as materially likely.

A deliberately low bar: EPSS is a 30-day probability, so a 10% chance of
exploitation inside a month is already an operational problem.
"""

CVSS_HIGH = 7.0


class Tier(StrEnum):
    """Remediation tier, with its service level."""

    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"

    @property
    def service_level(self) -> str:
        return {
            Tier.P0: "Emergency change; hours.",
            Tier.P1: "Days; tracked daily.",
            Tier.P2: "Next scheduled release.",
            Tier.P3: "Documented; reviewed quarterly.",
        }[self]


@dataclass(frozen=True)
class Finding:
    """One vulnerability as it applies to one asset."""

    cve: str
    component: str
    cvss: float
    epss: float
    in_kev: bool = False
    reachable: bool = True
    internet_facing: bool = False
    handles_personal_data: bool = False
    vex_refuted: bool = False


@dataclass(frozen=True)
class TriageResult:
    """A tiered finding, with the signal that decided it."""

    finding: Finding
    tier: Tier
    rationale: str

    @property
    def service_level(self) -> str:
        return self.tier.service_level


def triage(finding: Finding) -> TriageResult:
    """Assign a tier by applying the four signals in precedence order.

    1. **KEV** — confirmed exploitation in the wild, verified by a human.
       An emergency regardless of any score.  KEV is a floor, not a ceiling:
       absence never proves safety, which is why the remaining signals still run.
    2. **EPSS** — likelihood of exploitation within thirty days.
    3. **Reachability** — including a published VEX refutation.
    4. **Asset context** — exposure and data sensitivity, the one signal no
       external score can supply.
    """
    f = finding

    if f.in_kev:
        return TriageResult(f, Tier.P0, "listed in the CISA KEV catalogue")

    if f.vex_refuted:
        return TriageResult(f, Tier.P3, "refuted by a published VEX statement for this product")
    if not f.reachable:
        return TriageResult(f, Tier.P3, "vulnerable code path is not reachable from this product")

    exposed = f.internet_facing or f.handles_personal_data
    if f.epss >= EPSS_HIGH and exposed:
        return TriageResult(
            f,
            Tier.P1,
            f"EPSS {f.epss:.2f} above {EPSS_HIGH:.2f}, reachable, on an exposed asset",
        )
    if f.epss >= EPSS_HIGH:
        return TriageResult(
            f, Tier.P2, f"EPSS {f.epss:.2f} above {EPSS_HIGH:.2f}, reachable, not exposed"
        )
    if f.cvss >= CVSS_HIGH and exposed:
        return TriageResult(f, Tier.P2, f"CVSS {f.cvss:.1f} high and reachable on an exposed asset")
    if f.cvss >= CVSS_HIGH:
        return TriageResult(f, Tier.P2, f"CVSS {f.cvss:.1f} high, reachable, not exposed")
    return TriageResult(f, Tier.P3, "reachable but low severity and low exploitation likelihood")
