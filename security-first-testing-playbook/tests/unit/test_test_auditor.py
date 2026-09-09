"""Slide 16/19 — detecting tests that verify nothing, including our own.

The last test here is the self-referential gate: it runs the auditor over this
repository's entire suite.  A repository that teaches against assertion-free
tests must not contain one.
"""

from __future__ import annotations

from pathlib import Path

from stplaybook.quality.test_auditor import Verdict, audit_source, audit_tree

SAMPLE = """
def test_creates_an_invoice():
    res = api.post("/invoices", payload)

def test_only_truthiness():
    res = api.post("/invoices", payload)
    assert res
    assert res.status

def test_specific_value():
    res = api.post("/invoices", payload)
    assert res.status == 201

def test_expected_exception():
    with pytest.raises(DailyLimitExceeded):
        account.transfer(to="0123456789", amount=huge)
"""


def _verdict_for(name: str) -> Verdict:
    findings = audit_source(SAMPLE, "sample.py")
    return next(f.verdict for f in findings if f.test_name == name)


def test_a_test_with_no_assertion_is_flagged_assertion_free() -> None:
    assert _verdict_for("test_creates_an_invoice") is Verdict.ASSERTION_FREE


def test_truthiness_only_assertions_are_flagged_weak() -> None:
    assert _verdict_for("test_only_truthiness") is Verdict.WEAK


def test_comparison_against_an_expected_value_is_strong() -> None:
    assert _verdict_for("test_specific_value") is Verdict.STRONG


def test_asserting_an_expected_exception_is_strong() -> None:
    assert _verdict_for("test_expected_exception") is Verdict.STRONG


def test_only_assertion_free_tests_fail_the_audit() -> None:
    findings = audit_source(SAMPLE, "sample.py")
    failures = [f.test_name for f in findings if f.is_failure]

    assert failures == ["test_creates_an_invoice"]


def test_this_repository_contains_no_assertion_free_tests(repo_root: Path) -> None:
    """The self-referential gate. Also wired into `make audit` and CI."""
    findings = audit_tree(repo_root / "tests")
    offenders = [f"{f.path}:{f.line} {f.test_name}" for f in findings if f.is_failure]

    assert offenders == []
    assert len(findings) > 40
