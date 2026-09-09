"""Bank-statement parser — the subject of the fuzz target.

Slide 34 states the fuzzing contract precisely: for *any* byte string, this
function either returns a consistent :class:`Statement` or raises
:class:`InvalidStatement`.  It never crashes, never hangs, and never executes
anything from the input.  That is a stronger oracle than "does not crash", and
it is what makes the fuzz target able to find logic faults as well as memory
faults.

Wire format, one record per line, pipe-delimited::

    H|NGN|<account-number>
    L|<description>|<amount-in-kobo>
    T|<total-in-kobo>
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from .errors import InvalidStatement
from .money import Naira

__all__ = ["MAX_STATEMENT_BYTES", "Statement", "StatementLine", "parse_bank_statement"]

MAX_STATEMENT_BYTES: Final = 64 * 1024
MAX_LINES: Final = 1_000
SUPPORTED_CURRENCIES: Final = frozenset({"NGN"})


@dataclass(frozen=True)
class StatementLine:
    """One debit or credit line."""

    description: str
    amount: Naira


@dataclass(frozen=True)
class Statement:
    """A parsed statement whose total is guaranteed to equal its lines."""

    account: str
    currency: str
    lines: tuple[StatementLine, ...]
    total: Naira


def parse_bank_statement(data: bytes) -> Statement:
    """Parse ``data``, or raise :class:`InvalidStatement`.

    Bounded in both input size and line count, so no input can cause the parser
    to hang — the ``never hangs`` half of the contract is enforced structurally
    rather than hoped for.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise InvalidStatement("input must be bytes")
    if len(data) > MAX_STATEMENT_BYTES:
        raise InvalidStatement(f"statement exceeds {MAX_STATEMENT_BYTES} bytes")

    try:
        text = bytes(data).decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InvalidStatement("input is not valid UTF-8", offset=exc.start) from exc

    rows = [row for row in text.split("\n") if row.strip()]
    if not rows:
        raise InvalidStatement("statement is empty")
    if len(rows) > MAX_LINES:
        raise InvalidStatement(f"statement exceeds {MAX_LINES} lines")

    header = rows[0].split("|")
    if len(header) != 3 or header[0] != "H":
        raise InvalidStatement("first record must be a three-field header")
    _, currency, account = header
    if currency not in SUPPORTED_CURRENCIES:
        raise InvalidStatement(f"unsupported currency {currency!r}")
    if not account.isdigit() or len(account) != 10:
        raise InvalidStatement("header account must be ten digits")

    if rows[-1].split("|")[0] != "T":
        raise InvalidStatement("last record must be a trailer")
    trailer = rows[-1].split("|")
    if len(trailer) != 2:
        raise InvalidStatement("trailer must have two fields")
    declared_total = _parse_kobo(trailer[1], "trailer total")

    lines: list[StatementLine] = []
    for index, row in enumerate(rows[1:-1], start=1):
        fields = row.split("|")
        if len(fields) != 3 or fields[0] != "L":
            raise InvalidStatement(f"record {index} is not a three-field line")
        description = fields[1]
        if len(description) > 140:
            raise InvalidStatement(f"record {index} description too long")
        lines.append(StatementLine(description, _parse_kobo(fields[2], f"record {index}")))

    computed = sum(line.amount.kobo for line in lines)
    if computed != declared_total.kobo:
        raise InvalidStatement(
            f"declared total {declared_total.kobo} does not match computed {computed}"
        )

    return Statement(
        account=account,
        currency=currency,
        lines=tuple(lines),
        total=declared_total,
    )


def _parse_kobo(raw: str, where: str) -> Naira:
    """Parse a non-negative integer number of kobo, or raise."""
    if not raw.isdigit():
        raise InvalidStatement(f"{where}: amount must be a non-negative integer of kobo")
    if len(raw) > 18:
        raise InvalidStatement(f"{where}: amount is implausibly large")
    return Naira.from_kobo(int(raw))
