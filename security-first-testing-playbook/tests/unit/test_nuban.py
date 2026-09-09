"""NUBAN check digits — the gap behind the slides' bare account strings."""

from __future__ import annotations

import random

import pytest

from stplaybook.errors import InvalidAccountNumber
from stplaybook.nuban import generate_nuban, is_valid_nuban, require_valid_nuban


def test_generated_account_numbers_validate(rng: random.Random) -> None:
    number = generate_nuban("058", rng)

    assert len(number) == 10
    assert is_valid_nuban(number, "058")


def test_altering_the_check_digit_invalidates_the_number(rng: random.Random) -> None:
    number = generate_nuban("058", rng)
    tampered = number[:-1] + str((int(number[-1]) + 1) % 10)

    assert not is_valid_nuban(tampered, "058")


def test_short_account_numbers_are_rejected_with_a_reason() -> None:
    with pytest.raises(InvalidAccountNumber) as err:
        require_valid_nuban("12345", "058")
    assert err.value.reason == "must be exactly ten digits"


def test_wrong_check_digit_is_reported_distinctly() -> None:
    with pytest.raises(InvalidAccountNumber) as err:
        require_valid_nuban("0000000000", "058")
    assert err.value.reason == "check digit does not match"
