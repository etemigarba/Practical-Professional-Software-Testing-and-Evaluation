"""Slide 15 — FIRST principles and Arrange-Act-Assert.

Each test states one claim about behaviour and has exactly one reason to fail.
The first test is the slide's own example, preserved verbatim in intent; the
ones after it verify the *cumulative* daily limit the slide implies but never
demonstrates (Phase A correction, slide 15).
"""

from __future__ import annotations

import pytest

from stplaybook.clock import FrozenClock
from stplaybook.errors import DailyLimitExceeded, InsufficientFunds
from stplaybook.ledger import Account
from stplaybook.money import Naira


def test_transfer_rejects_amount_above_daily_limit(account: Account) -> None:
    # Arrange — the smallest world in which the rule is meaningful (the fixture)

    # Act — exactly one call; the behaviour under test
    with pytest.raises(DailyLimitExceeded) as err:
        account.transfer(to="0123456789", amount=Naira(200_001))

    # Assert — on the observable contract, not the implementation
    assert err.value.limit == Naira(200_000)
    assert account.balance == Naira(500_000)  # nothing was mutated


def test_transfer_within_limit_debits_exactly_once(account: Account) -> None:
    completed = account.transfer(to="0123456789", amount=Naira(150_000))

    assert completed.amount == Naira(150_000)
    assert account.balance == Naira(350_000)
    assert len(account.history()) == 1


def test_daily_limit_is_cumulative_not_per_transaction(account: Account) -> None:
    """The correction: two lawful transfers may together breach the limit."""
    account.transfer(to="0123456789", amount=Naira(150_000))

    with pytest.raises(DailyLimitExceeded) as err:
        account.transfer(to="0123456789", amount=Naira(60_000))

    assert err.value.already_spent == Naira(150_000)
    assert account.balance == Naira(350_000)


def test_daily_limit_resets_on_the_next_calendar_day(account: Account, clock: FrozenClock) -> None:
    account.transfer(to="0123456789", amount=Naira(200_000))
    clock.advance(days=1)

    account.transfer(to="0123456789", amount=Naira(120_000))

    assert account.balance == Naira(180_000)
    assert account.spent_today() == Naira(120_000)


def test_transfer_exceeding_balance_is_rejected_atomically(clock: FrozenClock) -> None:
    account = Account(balance=Naira(1_000), daily_limit=Naira(1_000_000), clock=clock)

    with pytest.raises(InsufficientFunds) as err:
        account.transfer(to="0123456789", amount=Naira(5_000))

    assert err.value.balance == Naira(1_000)
    assert account.history() == ()
