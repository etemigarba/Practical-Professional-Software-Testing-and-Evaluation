"""Slide 34 — a coverage-guided fuzz target for the statement parser.

Run it explicitly; it is never part of the default suite::

    STP_ENABLE_FUZZ=1 python tests/fuzz/fuzz_statement_parser.py -atheris_runs=200000

**Correction to slide 34.**  The slide calls ``atheris.Setup`` and
``atheris.Fuzz`` without instrumenting the subject.  Without
``instrument_imports`` the fuzzer receives no coverage feedback and degrades to
random input generation, losing the very property that makes it worth running.

The oracle is deliberately stronger than "does not crash": the parser must
either raise :class:`InvalidStatement` or return a statement whose declared total
equals the sum of its lines.  That catches logic faults, not only memory faults.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import atheris

with atheris.instrument_imports():
    from stplaybook.errors import InvalidStatement
    from stplaybook.parsing import SUPPORTED_CURRENCIES, parse_bank_statement


def TestOneInput(data: bytes) -> None:  # noqa: N802 - the name libFuzzer requires
    """Any byte string must either parse cleanly or be rejected by name."""
    try:
        statement = parse_bank_statement(data)
    except InvalidStatement:
        return

    if statement.total.kobo != sum(line.amount.kobo for line in statement.lines):
        raise AssertionError("parser returned a statement whose total does not balance")
    if statement.currency not in SUPPORTED_CURRENCIES:
        raise AssertionError(f"parser accepted unsupported currency {statement.currency!r}")
    if len(statement.account) != 10:
        raise AssertionError("parser accepted a malformed account number")


def main() -> None:
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
