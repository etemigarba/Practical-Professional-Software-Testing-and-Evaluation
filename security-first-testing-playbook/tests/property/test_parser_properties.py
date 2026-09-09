"""The parser contract as a property: parse or raise, never anything else.

Slide 34's oracle, stated as a Hypothesis property rather than a fuzz target, so
it runs in the default offline suite.  The Atheris target in ``tests/fuzz``
applies the same oracle with a coverage-guided generator.
"""

from __future__ import annotations

import random

import pytest
from hypothesis import given
from hypothesis import strategies as st

from stplaybook.errors import InvalidStatement
from stplaybook.parsing import parse_bank_statement
from tests.factories import make_statement_bytes


@given(data=st.binary(max_size=2048))
def test_arbitrary_bytes_either_parse_or_raise_invalid_statement(data: bytes) -> None:
    """The whole contract. Any other outcome is a defect."""
    try:
        statement = parse_bank_statement(data)
    except InvalidStatement:
        return

    assert statement.currency == "NGN"
    assert statement.total.kobo == sum(line.amount.kobo for line in statement.lines)


@given(data=st.text(max_size=512).map(str.encode))
def test_arbitrary_text_never_escapes_the_contract(data: bytes) -> None:
    try:
        statement = parse_bank_statement(data)
    except InvalidStatement:
        return

    assert len(statement.account) == 10


@given(seed=st.integers(min_value=0, max_value=10**6), lines=st.integers(1, 20))
def test_well_formed_statements_always_parse(seed: int, lines: int) -> None:
    """The positive direction: valid input is never spuriously rejected."""
    data = make_statement_bytes(random.Random(seed), lines=lines)

    statement = parse_bank_statement(data)

    assert len(statement.lines) == lines
    assert statement.total.kobo == sum(line.amount.kobo for line in statement.lines)


# Pinned crash reproducers, committed as ordinary regression tests so they run
# in the default suite forever after (slide 34: keep the corpus).
def test_pinned_truncated_header_is_rejected() -> None:
    with pytest.raises(InvalidStatement) as err:
        parse_bank_statement(b"H|NGN")

    assert "three-field header" in err.value.reason


def test_pinned_total_mismatch_is_rejected() -> None:
    with pytest.raises(InvalidStatement) as err:
        parse_bank_statement(b"H|NGN|1043321818\nL|a|1\nT|2")

    assert "does not match computed" in err.value.reason
