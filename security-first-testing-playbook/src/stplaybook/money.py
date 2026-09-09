"""Naira as a value object over integer kobo.

Slide 15 writes ``Naira(500_000)`` without stating the unit.  Silent unit
confusion is the classic money defect, so the convention is fixed here and
enforced by the type: **the constructor takes naira; the internal representation
is integer kobo.**  Floating point never touches an amount.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from functools import total_ordering
from typing import Final

from .errors import CurrencyMismatch, FractionalNaira, InvalidPartyCount, NegativeAmount

__all__ = ["KOBO_PER_NAIRA", "Naira", "split_bill"]

KOBO_PER_NAIRA: Final = 100


@total_ordering
class Naira:
    """An exact Nigerian Naira amount, stored as a whole number of kobo.

    ``Naira(500_000)`` is five hundred thousand naira.  Use
    :meth:`from_kobo` when the source value is already in the minor unit.
    """

    __slots__ = ("_kobo",)
    currency: Final = "NGN"

    def __init__(self, naira: int | str | Decimal) -> None:
        amount = Decimal(str(naira)) * KOBO_PER_NAIRA
        kobo = int(amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        if kobo < 0:
            raise NegativeAmount(kobo)
        self._kobo = kobo

    @classmethod
    def from_kobo(cls, kobo: int) -> Naira:
        """Build an amount directly from the minor unit."""
        if kobo < 0:
            raise NegativeAmount(kobo)
        instance = cls.__new__(cls)
        object.__setattr__(instance, "_kobo", int(kobo))
        return instance

    @property
    def kobo(self) -> int:
        """The amount as a whole number of kobo."""
        return self._kobo

    @property
    def naira(self) -> Decimal:
        """The amount as an exact decimal number of naira."""
        return Decimal(self._kobo) / KOBO_PER_NAIRA

    def to_naira_int(self) -> int:
        """Return whole naira, refusing to silently discard kobo.

        Slide 16 asserts ``total: 45_000`` against the API boundary, so the
        boundary must emit whole naira.  Truncating here would be exactly the
        silent rounding error the deck warns about, hence the explicit refusal.
        """
        if self._kobo % KOBO_PER_NAIRA:
            raise FractionalNaira(self._kobo)
        return self._kobo // KOBO_PER_NAIRA

    def __add__(self, other: Naira) -> Naira:
        self._require_same_currency(other)
        return Naira.from_kobo(self._kobo + other._kobo)

    def __sub__(self, other: Naira) -> Naira:
        self._require_same_currency(other)
        return Naira.from_kobo(self._kobo - other._kobo)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Naira):
            return NotImplemented
        return self._kobo == other._kobo

    def __lt__(self, other: Naira) -> bool:
        self._require_same_currency(other)
        return self._kobo < other._kobo

    def __hash__(self) -> int:
        return hash((self.currency, self._kobo))

    def __repr__(self) -> str:
        return f"Naira.from_kobo({self._kobo})"

    def __str__(self) -> str:
        return f"\u20a6{self.naira:,.2f}"

    def _require_same_currency(self, other: Naira) -> None:
        if not isinstance(other, Naira):
            raise CurrencyMismatch(self.currency, type(other).__name__)


def split_bill(total: Naira, parties: int) -> list[Naira]:
    """Divide ``total`` between ``parties`` using largest-remainder allocation.

    Two properties hold for every input, and both are asserted in
    ``tests/property/test_money_properties.py``:

    * **conservation** — the shares sum to exactly ``total``; no kobo is
      created or destroyed;
    * **fairness** — no two shares differ by more than one kobo.

    Slide 18 states the fairness property without naming the algorithm that
    guarantees it.  Largest remainder is that algorithm: give everyone the floor
    share, then distribute the remaining kobo one each to the first ``r``
    parties.
    """
    if parties < 1:
        raise InvalidPartyCount(parties)
    base, remainder = divmod(total.kobo, parties)
    return [Naira.from_kobo(base + (1 if i < remainder else 0)) for i in range(parties)]
