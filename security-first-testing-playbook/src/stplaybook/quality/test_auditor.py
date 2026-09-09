"""Detect tests that execute code without verifying anything.

Slide 16 names the failure mode and slide 19 explains why it now matters:
machine-generated suites raise coverage almost for free, and coverage without
meaningful assertions is a false signal.  This module finds those tests
statically, so the repository can gate on their absence.

Three verdicts:

``ASSERTION_FREE``
    No assertion of any kind.  The test proves only that the code did not raise.
``WEAK``
    Assertions exist, but every one of them is satisfied by almost any value —
    ``assert x``, ``assert x is not None``, ``assert isinstance(...)`` alone, or
    an assertion made solely against a mock's call record.
``STRONG``
    At least one assertion compares against a specific expected value, or
    asserts a specific exception type.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

__all__ = ["AuditFinding", "Verdict", "audit_file", "audit_source", "audit_tree"]

_MOCK_ASSERTIONS = frozenset(
    {
        "assert_called",
        "assert_called_once",
        "assert_called_with",
        "assert_called_once_with",
        "assert_any_call",
        "assert_has_calls",
    }
)
_WEAK_UNITTEST = frozenset({"assertTrue", "assertFalse", "assertIsNotNone", "assertIsNone"})


class Verdict(StrEnum):
    """How much a test actually verifies."""

    STRONG = "strong"
    WEAK = "weak"
    ASSERTION_FREE = "assertion_free"


@dataclass(frozen=True)
class AuditFinding:
    """One test function and what it was found to verify."""

    path: str
    test_name: str
    line: int
    verdict: Verdict
    detail: str

    @property
    def is_failure(self) -> bool:
        """Assertion-free tests fail the audit; weak ones are reported only."""
        return self.verdict is Verdict.ASSERTION_FREE


def _is_specific(node: ast.expr) -> bool:
    """True when an assertion compares against a concrete expected value."""
    if isinstance(node, ast.Compare):
        return True
    if isinstance(node, ast.BoolOp):
        return any(_is_specific(v) for v in node.values)
    if isinstance(node, ast.Call):
        func = node.func
        name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
        if name in _MOCK_ASSERTIONS or name in _WEAK_UNITTEST:
            return False
        if name.startswith("assert") and name not in _WEAK_UNITTEST:
            return True
    return False


def _classify(func: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[Verdict, str]:
    asserts: list[ast.Assert] = []
    raises_ctx = 0
    calls: list[ast.Call] = []

    for node in ast.walk(func):
        if isinstance(node, ast.Assert):
            asserts.append(node)
        elif isinstance(node, ast.Call):
            calls.append(node)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                ctx = item.context_expr
                if isinstance(ctx, ast.Call):
                    target = ctx.func
                    attr = target.attr if isinstance(target, ast.Attribute) else ""
                    if attr in {"raises", "warns", "assertRaises"}:
                        raises_ctx += 1

    method_asserts = [
        c for c in calls if isinstance(c.func, ast.Attribute) and c.func.attr.startswith("assert")
    ]

    if not asserts and not raises_ctx and not method_asserts:
        return Verdict.ASSERTION_FREE, "no assertion, no expected exception"

    if raises_ctx and any(_is_specific(a.test) for a in asserts):
        return Verdict.STRONG, "asserts an expected exception and a specific value"
    if raises_ctx:
        return Verdict.STRONG, "asserts a specific expected exception"
    if any(_is_specific(a.test) for a in asserts):
        return Verdict.STRONG, f"{len(asserts)} assertion(s), at least one specific"
    if any(_is_specific(ast.Expr(value=c).value) for c in method_asserts):
        return Verdict.STRONG, "specific assertion method"
    return Verdict.WEAK, "assertions present but none compares against an expected value"


def audit_source(source: str, path: str = "<string>") -> list[AuditFinding]:
    """Audit every ``test_*`` function in a module's source."""
    tree = ast.parse(source)
    findings: list[AuditFinding] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith(
            "test_"
        ):
            verdict, detail = _classify(node)
            findings.append(AuditFinding(path, node.name, node.lineno, verdict, detail))
    return findings


def audit_file(path: Path) -> list[AuditFinding]:
    """Audit one test module on disk."""
    return audit_source(path.read_text(encoding="utf-8"), str(path))


def audit_tree(root: Path) -> list[AuditFinding]:
    """Audit every ``test_*.py`` beneath ``root``, sorted for stable output."""
    findings: list[AuditFinding] = []
    for path in sorted(root.rglob("test_*.py")):
        findings.extend(audit_file(path))
    return findings
