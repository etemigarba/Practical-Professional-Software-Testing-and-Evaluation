"""Slide 35 — SBOM, VEX and provenance answer four different questions.

SBOM: what is inside.  SLSA provenance: how it was built.  Sigstore: who vouches
for it.  VEX: which of the CVEs advertised against those components actually
matter here.  None substitutes for another, which is why each has its own tests.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from stplaybook.errors import ProvenanceRejected, SbomError
from stplaybook.security.provenance import sha256_of, verify_provenance
from stplaybook.security.sbom import load_sbom, parse_sbom
from stplaybook.security.triage import Tier, triage
from stplaybook.security.vex import VexStatus, apply_vex, load_vex
from tests.factories import make_finding

PRODUCT = "security-first-testing-playbook@1.0.0"
ARTEFACT_NAME = "security_first_testing_playbook-1.0.0-py3-none-any.whl"
TRUSTED = frozenset({"https://github.com/actions/runner/github-hosted"})
EXPECTED_SOURCE = (
    "git+https://github.com/etemigarba/security-first-testing-playbook@refs/tags/v1.0.0"
)


# --- SBOM: what is inside -------------------------------------------------


def test_sbom_lists_every_component_with_a_version(golden: Path) -> None:
    sbom = load_sbom(golden / "sbom.cdx.json")

    assert sbom.spec_version == "1.6"
    assert len(sbom.components) == 3
    assert "libexample@2.4.1" in sbom.coordinates()


def test_sbom_surfaces_a_forbidden_licence(golden: Path) -> None:
    """The licence policy check on slide 36's pre-release gate."""
    sbom = load_sbom(golden / "sbom.cdx.json")

    offending = sbom.forbidden_licences(frozenset({"AGPL-3.0-only"}))

    assert [c.name for c in offending] == ["copyleft-widget"]


def test_a_document_that_is_not_cyclonedx_is_refused() -> None:
    with pytest.raises(SbomError) as err:
        parse_sbom('{"bomFormat": "SPDX", "specVersion": "2.3"}')
    assert "CycloneDX" in err.value.reason


def test_a_component_without_a_version_is_refused() -> None:
    document = '{"bomFormat":"CycloneDX","specVersion":"1.6","components":[{"name":"x"}]}'

    with pytest.raises(SbomError) as err:
        parse_sbom(document)
    assert "version" in err.value.reason


# --- VEX: which CVEs actually matter --------------------------------------


def test_a_justified_not_affected_statement_refutes_a_finding(golden: Path) -> None:
    statements = load_vex(golden / "vex.csaf.json")
    findings = [make_finding("CVE-2026-0004", cvss=9.8, epss=0.9)]

    annotated = apply_vex(findings, statements, product=PRODUCT)

    assert annotated[0].vex_refuted is True
    assert triage(annotated[0]).tier is Tier.P3


def test_an_unjustified_not_affected_statement_refutes_nothing(golden: Path) -> None:
    """An unjustified refutation is an opinion, not evidence."""
    statements = load_vex(golden / "vex.csaf.json")
    unjustified = next(s for s in statements if s.cve == "CVE-2026-0009")

    assert unjustified.status is VexStatus.NOT_AFFECTED
    assert unjustified.refutes is False


def test_an_affected_statement_leaves_the_finding_untouched(golden: Path) -> None:
    statements = load_vex(golden / "vex.csaf.json")
    findings = [make_finding("CVE-2026-0002", cvss=7.5, epss=0.62, internet_facing=True)]

    annotated = apply_vex(findings, statements, product=PRODUCT)

    assert annotated[0].vex_refuted is False
    assert triage(annotated[0]).tier is Tier.P1


def test_vex_annotates_rather_than_deletes(golden: Path) -> None:
    """A suppressed finding that leaves no trace looks like one nobody examined."""
    statements = load_vex(golden / "vex.csaf.json")
    findings = [make_finding("CVE-2026-0004"), make_finding("CVE-2026-0002")]

    annotated = apply_vex(findings, statements, product=PRODUCT)

    assert len(annotated) == 2


# --- Provenance: how it was built -----------------------------------------


def test_matching_artefact_and_attestation_verify(golden: Path) -> None:
    check = verify_provenance(
        artefact_bytes=(golden / "artefact.bin").read_bytes(),
        artefact_name=ARTEFACT_NAME,
        attestation=(golden / "provenance.intoto.json").read_text(),
        trusted_builders=TRUSTED,
        expected_source=EXPECTED_SOURCE,
    )

    assert check.verified is True
    assert check.reasons == ()


def test_a_tampered_artefact_is_rejected_on_digest(golden: Path) -> None:
    """Slide 29's tampering abuse case: swapped between build and deploy."""
    check = verify_provenance(
        artefact_bytes=b"replaced payload",
        artefact_name=ARTEFACT_NAME,
        attestation=(golden / "provenance.intoto.json").read_text(),
        trusted_builders=TRUSTED,
        expected_source=EXPECTED_SOURCE,
    )

    assert check.verified is False
    assert any("digest mismatch" in reason for reason in check.reasons)


def test_an_untrusted_builder_is_rejected(golden: Path) -> None:
    check = verify_provenance(
        artefact_bytes=(golden / "artefact.bin").read_bytes(),
        artefact_name=ARTEFACT_NAME,
        attestation=(golden / "provenance.intoto.json").read_text(),
        trusted_builders=frozenset({"https://example.invalid/builder"}),
        expected_source=EXPECTED_SOURCE,
    )

    assert check.verified is False
    assert any("not in the trusted set" in reason for reason in check.reasons)


def test_verification_fails_closed_and_reports_every_deviation(golden: Path) -> None:
    check = verify_provenance(
        artefact_bytes=b"replaced payload",
        artefact_name=ARTEFACT_NAME,
        attestation=(golden / "provenance.intoto.json").read_text(),
        trusted_builders=frozenset({"https://example.invalid/builder"}),
        expected_source="git+https://example.invalid/other",
    )

    assert check.verified is False
    assert len(check.reasons) == 3


def test_an_attestation_that_is_not_in_toto_is_refused() -> None:
    with pytest.raises(ProvenanceRejected) as err:
        verify_provenance(
            artefact_bytes=b"x",
            artefact_name="x",
            attestation='{"_type": "https://example.invalid/other"}',
            trusted_builders=TRUSTED,
            expected_source=EXPECTED_SOURCE,
        )
    assert "in-toto" in err.value.reason


def test_digest_helper_matches_the_committed_fixture(golden: Path) -> None:
    artefact = (golden / "artefact.bin").read_bytes()
    attestation = (golden / "provenance.intoto.json").read_text()

    assert sha256_of(artefact) in attestation
