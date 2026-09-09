"""A Naira ledger with tenant scoping and a cumulative daily limit.

**Correction to slide 15.**  The slide asserts ``DailyLimitExceeded`` after a
single transfer, which only breaches a *daily* limit because prior spend happens
to be zero.  As printed it verifies a per-transaction cap while claiming to
verify a daily one.  Here the limit is genuinely cumulative across a UTC
calendar day, measured against an injected clock, so the rule the deck describes
is the rule the tests exercise.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .clock import Clock, SystemClock
from .errors import DailyLimitExceeded, InsufficientFunds
from .money import Naira
from .nuban import require_valid_nuban

__all__ = ["Account", "Transfer"]


@dataclass(frozen=True)
class Transfer:
    """A completed movement of funds."""

    to: str
    amount: Naira
    on: date


class Account:
    """A single account, scoped to one tenant, with a cumulative daily limit."""

    def __init__(
        self,
        *,
        balance: Naira,
        daily_limit: Naira,
        tenant: str = "default",
        number: str = "0000000000",
        bank_code: str = "058",
        clock: Clock | None = None,
    ) -> None:
        self._balance = balance
        self._daily_limit = daily_limit
        self.tenant = tenant
        self.number = number if number == "0000000000" else require_valid_nuban(number, bank_code)
        self._clock: Clock = clock or SystemClock()
        self._transfers: list[Transfer] = []

    @property
    def balance(self) -> Naira:
        """Funds currently available."""
        return self._balance

    @property
    def daily_limit(self) -> Naira:
        """The maximum that may be transferred out in one UTC calendar day."""
        return self._daily_limit

    def spent_on(self, day: date) -> Naira:
        """Total transferred out on ``day``."""
        total = Naira.from_kobo(0)
        for transfer in self._transfers:
            if transfer.on == day:
                total = total + transfer.amount
        return total

    def spent_today(self) -> Naira:
        """Total transferred out so far today."""
        return self.spent_on(self._clock.today())

    def history(self) -> tuple[Transfer, ...]:
        """Every completed transfer, oldest first."""
        return tuple(self._transfers)

    def transfer(self, *, to: str, amount: Naira) -> Transfer:
        """Move ``amount`` to ``to``.

        Raises :class:`DailyLimitExceeded` when the transfer would push today's
        cumulative outgoings past the limit, and :class:`InsufficientFunds` when
        the balance cannot cover it.  Either way **nothing is mutated** — the
        operation is atomic, which is what the second assertion on slide 15
        exists to prove.
        """
        today = self._clock.today()
        already = self.spent_on(today)
        if (already + amount) > self._daily_limit:
            raise DailyLimitExceeded(
                limit=self._daily_limit, already_spent=already, attempted=amount
            )
        if amount > self._balance:
            raise InsufficientFunds(balance=self._balance, attempted=amount)

        completed = Transfer(to=to, amount=amount, on=today)
        self._balance = self._balance - amount
        self._transfers.append(completed)
        return completed
