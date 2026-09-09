"""NUBAN check digits, as properties over the whole generated space."""

from __future__ import annotations

import random

from hypothesis import given
from hypothesis import strategies as st

from stplaybook.nuban import check_digit, generate_nuban, is_valid_nuban

serials = st.text(alphabet="0123456789", min_size=9, max_size=9)
bank_codes = st.text(alphabet="0123456789", min_size=3, max_size=3)


@given(bank_code=bank_codes, serial=serials)
def test_check_digit_is_always_a_single_digit(bank_code: str, serial: str) -> None:
    assert 0 <= check_digit(bank_code, serial) <= 9


@given(bank_code=bank_codes, serial=serials)
def test_appending_the_check_digit_always_yields_a_valid_number(
    bank_code: str, serial: str
) -> None:
    number = serial + str(check_digit(bank_code, serial))

    assert is_valid_nuban(number, bank_code)


@given(seed=st.integers(min_value=0, max_value=10**6), offset=st.integers(1, 9))
def test_any_single_digit_change_to_the_check_digit_invalidates(seed: int, offset: int) -> None:
    """A check digit that tolerated a change would not be a check digit."""
    number = generate_nuban("058", random.Random(seed))
    tampered = number[:-1] + str((int(number[-1]) + offset) % 10)

    assert not is_valid_nuban(tampered, "058")
