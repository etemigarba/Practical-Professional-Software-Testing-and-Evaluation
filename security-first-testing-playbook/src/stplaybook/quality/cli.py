"""Command line for the test auditor.

``python -m stplaybook.quality.cli audit tests`` fails the build when any test
in the tree asserts nothing.  Wired into ``make audit`` and the CI gate, so this
repository cannot ship the failure mode it teaches against.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .test_auditor import Verdict, audit_tree

__all__ = ["main"]


def main(argv: list[str] | None = None) -> int:
    """Audit a test tree. Returns 0 when clean, 1 when an assertion-free test exists."""
    parser = argparse.ArgumentParser(prog="stplaybook-audit", description=__doc__)
    parser.add_argument("command", choices=["audit"])
    parser.add_argument("path", type=Path)
    parser.add_argument(
        "--show-weak", action="store_true", help="also list weak (but not failing) tests"
    )
    args = parser.parse_args(argv)

    findings = audit_tree(args.path)
    failures = [f for f in findings if f.is_failure]
    weak = [f for f in findings if f.verdict is Verdict.WEAK]

    print(f"Audited {len(findings)} test(s) under {args.path}")
    if args.show_weak and weak:
        print(f"\n{len(weak)} weak test(s):")
        for f in weak:
            print(f"  {f.path}:{f.line} {f.test_name} — {f.detail}")

    if failures:
        print(f"\n{len(failures)} assertion-free test(s):")
        for f in failures:
            print(f"  {f.path}:{f.line} {f.test_name} — {f.detail}")
        return 1

    print("No assertion-free tests found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
