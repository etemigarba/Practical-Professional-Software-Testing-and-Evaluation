"""Slide 17 — five kinds of double, three legitimate uses.

The slide's closing rule is the one worth proving: prefer a fake over a mock,
because a mock encodes your belief about a collaborator while a fake can be
tested against the real contract.
"""

from __future__ import annotations

from dataclasses import dataclass

from stplaybook.money import Naira


class AuditLog:
    """The collaborator under substitution."""

    def record(self, event: str, amount: Naira) -> None:  # pragma: no cover - real impl
        raise RuntimeError(
            f"the real audit log is not available in a unit test "
            f"(would have recorded {event} of {amount})"
        )


@dataclass
class SpyAuditLog:
    """A spy: the call itself is the observable outcome, so recording is valid."""

    calls: list[tuple[str, Naira]]

    def record(self, event: str, amount: Naira) -> None:
        self.calls.append((event, amount))


class FakeAuditLog:
    """A fake: a working lightweight implementation with real query behaviour."""

    def __init__(self) -> None:
        self._events: list[tuple[str, Naira]] = []

    def record(self, event: str, amount: Naira) -> None:
        self._events.append((event, amount))

    def total_for(self, event: str) -> Naira:
        total = Naira.from_kobo(0)
        for name, amount in self._events:
            if name == event:
                total = total + amount
        return total


def test_spy_is_appropriate_when_the_call_is_the_outcome() -> None:
    """An audit trail's whole purpose is that the call happened."""
    spy = SpyAuditLog(calls=[])

    spy.record("transfer", Naira(50_000))

    assert spy.calls == [("transfer", Naira(50_000))]


def test_fake_supports_assertions_about_state_not_interactions() -> None:
    """The fake answers a question about the world; a mock could not."""
    fake = FakeAuditLog()

    fake.record("transfer", Naira(50_000))
    fake.record("transfer", Naira(25_000))
    fake.record("refund", Naira(10_000))

    assert fake.total_for("transfer") == Naira(75_000)
    assert fake.total_for("refund") == Naira(10_000)


def test_fake_and_spy_agree_on_the_recorded_events() -> None:
    """A fake must not drift from the contract the spy observes."""
    spy, fake = SpyAuditLog(calls=[]), FakeAuditLog()

    for double in (spy, fake):
        double.record("transfer", Naira(1_000))

    assert spy.calls == [("transfer", Naira(1_000))]
    assert fake.total_for("transfer") == Naira(1_000)
