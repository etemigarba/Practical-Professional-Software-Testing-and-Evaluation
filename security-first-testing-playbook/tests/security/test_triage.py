"""Slide 47 — four signals, in order."""

from __future__ import annotations

from stplaybook.security.triage import Tier, triage
from tests.factories import make_finding


def test_kev_membership_is_an_emergency_regardless_of_score() -> None:
    result = triage(make_finding("CVE-2026-0001", cvss=3.1, epss=0.001, in_kev=True))

    assert result.tier is Tier.P0
    assert result.service_level == "Emergency change; hours."


def test_high_epss_on_an_exposed_asset_outranks_a_higher_cvss() -> None:
    """Slide 47's exact claim, as an executable comparison."""
    likely = triage(make_finding("CVE-2026-0002", cvss=7.5, epss=0.94, internet_facing=True))
    severe_but_improbable = triage(
        make_finding("CVE-2026-0003", cvss=9.1, epss=0.003, internet_facing=True)
    )

    assert likely.tier is Tier.P1
    assert severe_but_improbable.tier is Tier.P2


def test_an_unreachable_vulnerability_is_documentation_not_an_incident() -> None:
    result = triage(make_finding("CVE-2026-0004", cvss=9.8, epss=0.8, reachable=False))

    assert result.tier is Tier.P3
    assert "not reachable" in result.rationale


def test_a_justified_vex_refutation_deprioritises_the_finding() -> None:
    result = triage(make_finding("CVE-2026-0005", cvss=9.8, epss=0.9, vex_refuted=True))

    assert result.tier is Tier.P3
    assert "VEX" in result.rationale


def test_asset_context_separates_two_identical_cves() -> None:
    """The signal no external score can supply."""
    exposed = triage(make_finding("CVE-2026-0006", cvss=7.5, epss=0.5, internet_facing=True))
    internal = triage(make_finding("CVE-2026-0006", cvss=7.5, epss=0.5))

    assert exposed.tier is Tier.P1
    assert internal.tier is Tier.P2


def test_kev_takes_precedence_over_a_vex_refutation() -> None:
    """Confirmed exploitation in the wild overrides a producer's own assertion."""
    result = triage(
        make_finding("CVE-2026-0007", cvss=5.0, epss=0.02, in_kev=True, vex_refuted=True)
    )

    assert result.tier is Tier.P0
