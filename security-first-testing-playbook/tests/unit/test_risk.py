"""Slide 10 — risk banding drives depth, and the reasoning is retained."""

from __future__ import annotations

from stplaybook.quality.risk import Band, Impact, Likelihood, Technique, assess, required_depth


def test_payment_authorisation_bands_critical() -> None:
    assessment = assess("payment authorisation", Impact.SEVERE, Likelihood.LIKELY)

    assert assessment.band is Band.CRITICAL
    assert Technique.PENETRATION_TEST in assessment.required_techniques
    assert assessment.release_rule == "No known critical or high findings."


def test_severe_impact_never_bands_below_high_however_rare() -> None:
    """Impact dominates: being wrong about likelihood is asymmetric."""
    assessment = assess("funds transfer", Impact.SEVERE, Likelihood.RARE)

    assert assessment.band is Band.HIGH


def test_static_content_bands_low_and_needs_only_smoke_tests() -> None:
    assessment = assess("static content", Impact.NEGLIGIBLE, Likelihood.RARE)

    assert assessment.band is Band.LOW
    assert assessment.required_techniques == frozenset({Technique.SMOKE})


def test_rationale_records_the_inputs_that_produced_the_band() -> None:
    """When an incident asks 'why was this medium?', the answer must exist."""
    assessment = assess("internal dashboard", Impact.MODERATE, Likelihood.OCCASIONAL)

    assert assessment.band is Band.MEDIUM
    assert "impact=moderate" in assessment.rationale
    assert "likelihood=occasional" in assessment.rationale


def test_higher_bands_require_everything_lower_bands_require() -> None:
    """Depth is monotonic; a critical component is never tested less than a high one."""
    assert required_depth(Band.HIGH) < required_depth(Band.CRITICAL)
    assert required_depth(Band.MEDIUM) < required_depth(Band.HIGH)
