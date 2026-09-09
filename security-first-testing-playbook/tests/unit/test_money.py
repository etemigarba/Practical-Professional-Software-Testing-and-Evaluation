"""The Naira value object: units are fixed by the type, not by convention."""

from __future__ import annotations

from decimal import Decimal

import pytest

from stplaybook.errors import FractionalNaira, InvalidPartyCount, NegativeAmount
from stplaybook.money import Naira, split_bill


def test_constructor_takes_naira_and_stores_kobo() -> None:
    assert Naira(500_000).kobo == 50_000_000


def test_from_kobo_takes_the_minor_unit() -> None:
    assert Naira.from_kobo(50_000_000) == Naira(500_000)


def test_subtraction_matches_the_slide_22_arithmetic() -> None:
    assert Naira(500_000) - Naira(50_000) == Naira(450_000)


def test_formatting_uses_the_naira_sign_and_two_decimals() -> None:
    assert str(Naira(450_000)) == "\u20a6450,000.00"


def test_decimal_input_is_exact() -> None:
    assert Naira(Decimal("1234.56")).kobo == 123_456


def test_negative_amounts_are_refused() -> None:
    with pytest.raises(NegativeAmount) as err:
        Naira(-1)
    assert err.value.kobo == -100


def test_subtraction_below_zero_is_refused() -> None:
    with pytest.raises(NegativeAmount):
        Naira(100) - Naira(500)


def test_whole_naira_accessor_refuses_to_discard_kobo() -> None:
    with pytest.raises(FractionalNaira) as err:
        Naira(Decimal("10.50")).to_naira_int()
    assert err.value.kobo == 1_050


def test_split_bill_conserves_every_kobo() -> None:
    shares = split_bill(Naira(100), parties=3)
    assert [s.kobo for s in shares] == [3334, 3333, 3333]
    assert sum(s.kobo for s in shares) == 10_000


def test_split_bill_refuses_fewer_than_one_party() -> None:
    with pytest.raises(InvalidPartyCount) as err:
        split_bill(Naira(100), parties=0)
    assert err.value.parties == 0
