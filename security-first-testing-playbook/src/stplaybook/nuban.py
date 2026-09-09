"""NUBAN account-number validation.

The slides use bare ten-digit strings such as ``"0123456789"``.  Nigeria's
Central Bank NUBAN scheme defines a check digit over the three-digit bank code
and nine-digit serial, so a valid-looking string is not necessarily a valid
account number.  Fixtures in this repository generate genuinely valid synthetic
numbers rather than plausible-looking ones.
"""

from __future__ import annotations

import random
from typing import Final

from .errors import InvalidAccountNumber

__all__ = ["NUBAN_LENGTH", "check_digit", "generate_nuban", "is_valid_nuban", "require_valid_nuban"]

NUBAN_LENGTH: Final = 10
_SERIAL_LENGTH: Final = 9
_BANK_CODE_LENGTH: Final = 3
_WEIGHTS: Final = (3, 7, 3, 3, 7, 3, 3, 7, 3, 3, 7, 3)


def check_digit(bank_code: str, serial: str) -> int:
    """Compute the NUBAN check digit for a bank code and nine-digit serial."""
    if len(bank_code) != _BANK_CODE_LENGTH or not bank_code.isdigit():
        raise InvalidAccountNumber(bank_code, "bank code must be three digits")
    if len(serial) != _SERIAL_LENGTH or not serial.isdigit():
        raise InvalidAccountNumber(serial, "serial must be nine digits")
    digits = [int(d) for d in bank_code + serial]
    total = sum(d * w for d, w in zip(digits, _WEIGHTS, strict=True))
    remainder = total % 10
    return 0 if remainder == 0 else 10 - remainder


def is_valid_nuban(account_number: str, bank_code: str) -> bool:
    """Return ``True`` when the account number's check digit is correct."""
    if len(account_number) != NUBAN_LENGTH or not account_number.isdigit():
        return False
    serial, supplied = account_number[:_SERIAL_LENGTH], int(account_number[-1])
    return check_digit(bank_code, serial) == supplied


def require_valid_nuban(account_number: str, bank_code: str) -> str:
    """Return the account number, or raise :class:`InvalidAccountNumber`."""
    if len(account_number) != NUBAN_LENGTH or not account_number.isdigit():
        raise InvalidAccountNumber(account_number, "must be exactly ten digits")
    if not is_valid_nuban(account_number, bank_code):
        raise InvalidAccountNumber(account_number, "check digit does not match")
    return account_number


def generate_nuban(bank_code: str, rng: random.Random) -> str:
    """Generate a synthetic but structurally valid NUBAN.

    Takes an explicit ``rng`` so that fixtures are reproducible; see slide 24 on
    controlling randomness rather than inheriting it.
    """
    serial = "".join(str(rng.randrange(10)) for _ in range(_SERIAL_LENGTH))
    return serial + str(check_digit(bank_code, serial))
