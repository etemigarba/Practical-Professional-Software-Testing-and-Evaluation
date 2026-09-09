"""Risk banding: impact x likelihood, then depth follows from the band.

Slide 10's argument is that exhaustive testing is impossible, so uniform testing
is always the wrong allocation.  The slide gives the bands as a table; here they
are computed, so the reasoning is inspectable when somebody later asks "why was
this rated medium?".
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum, StrEnum

__all__ = [
    "Band",
    "Impact",
    "Likelihood",
    "RiskAssessment",
    "Technique",
    "assess",
    "release_rule",
    "required_depth",
]


class Impact(IntEnum):
    """Loss if this fails: financial, regulatory, safety, reputational."""

    NEGLIGIBLE = 1
    MODERATE = 2
    SERIOUS = 3
    SEVERE = 4


class Likelihood(IntEnum):
    """Driven by change rate, complexity, defect history and exposure."""

    RARE = 1
    OCCASIONAL = 2
    LIKELY = 3
    FREQUENT = 4


class Band(StrEnum):
    """The four bands the deck uses."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Technique(StrEnum):
    """Test techniques a band may require."""

    SMOKE = "smoke"
    UNIT = "unit"
    INTEGRATION = "integration"
    CONTRACT = "contract"
    PROPERTY = "property"
    MUTATION = "mutation"
    SAST_SCA = "sast+sca"
    DAST = "dast"
    PENETRATION_TEST = "penetration-test"


_DEPTH: dict[Band, frozenset[Technique]] = {
    Band.LOW: frozenset({Technique.SMOKE}),
    Band.MEDIUM: frozenset({Technique.UNIT, Technique.INTEGRATION}),
    Band.HIGH: frozenset(
        {Technique.UNIT, Technique.INTEGRATION, Technique.CONTRACT, Technique.SAST_SCA}
    ),
    Band.CRITICAL: frozenset(
        {
            Technique.UNIT,
            Technique.INTEGRATION,
            Technique.CONTRACT,
            Technique.PROPERTY,
            Technique.MUTATION,
            Technique.SAST_SCA,
            Technique.DAST,
            Technique.PENETRATION_TEST,
        }
    ),
}

_RELEASE_RULE: dict[Band, str] = {
    Band.LOW: "Team discretion.",
    Band.MEDIUM: "Documented acceptance by the team lead.",
    Band.HIGH: "No known critical findings.",
    Band.CRITICAL: "No known critical or high findings.",
}


@dataclass(frozen=True)
class RiskAssessment:
    """A banded component, with the reasoning kept alongside the verdict."""

    component: str
    impact: Impact
    likelihood: Likelihood
    band: Band
    rationale: str

    @property
    def required_techniques(self) -> frozenset[Technique]:
        return required_depth(self.band)

    @property
    def release_rule(self) -> str:
        return release_rule(self.band)


def assess(component: str, impact: Impact, likelihood: Likelihood) -> RiskAssessment:
    """Band a component from its impact and likelihood scores.

    Impact dominates deliberately: a severe-impact component is never below
    high, however rarely it is expected to fail, because the cost of being wrong
    about the likelihood is asymmetric.
    """
    score = impact * likelihood
    if impact is Impact.SEVERE and likelihood >= Likelihood.OCCASIONAL:
        band = Band.CRITICAL
    elif impact is Impact.SEVERE:
        band = Band.HIGH
    elif score >= 9:
        band = Band.CRITICAL
    elif score >= 6:
        band = Band.HIGH
    elif score >= 3:
        band = Band.MEDIUM
    else:
        band = Band.LOW
    rationale = (
        f"impact={impact.name.lower()} x likelihood={likelihood.name.lower()} "
        f"(score {score}) -> {band.value}"
    )
    return RiskAssessment(component, impact, likelihood, band, rationale)


def required_depth(band: Band) -> frozenset[Technique]:
    """The techniques a band obliges. Higher bands are supersets of lower ones."""
    return _DEPTH[band]


def release_rule(band: Band) -> str:
    """The condition under which a component in this band may ship."""
    return _RELEASE_RULE[band]
