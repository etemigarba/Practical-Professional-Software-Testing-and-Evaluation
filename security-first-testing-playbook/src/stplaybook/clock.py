"""Injectable clocks.

Slide 24 makes the case plainly: a test that fails at month end, in another
timezone, or once in fifty runs is a design defect rather than bad luck.  Every
time-dependent component in this package accepts a :class:`Clock`.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Protocol, runtime_checkable

__all__ = ["Clock", "FrozenClock", "SystemClock"]


@runtime_checkable
class Clock(Protocol):
    """The only source of time any component in this package may consult."""

    def now(self) -> datetime:
        """Return the current instant as a timezone-aware UTC datetime."""
        ...

    def today(self) -> date:
        """Return the current UTC calendar date."""
        ...


class SystemClock:
    """Reads the real clock. The production default; never used in tests."""

    def now(self) -> datetime:
        return datetime.now(UTC)

    def today(self) -> date:
        return self.now().date()


class FrozenClock:
    """A clock that returns a fixed instant until explicitly advanced."""

    def __init__(self, instant: datetime) -> None:
        if instant.tzinfo is None:
            raise ValueError("FrozenClock requires a timezone-aware datetime")
        self._instant = instant.astimezone(UTC)

    def now(self) -> datetime:
        return self._instant

    def today(self) -> date:
        return self._instant.date()

    def advance(self, *, days: int = 0, hours: int = 0, minutes: int = 0) -> None:
        """Move the clock forward. Time never runs backwards."""
        from datetime import timedelta

        delta = timedelta(days=days, hours=hours, minutes=minutes)
        if delta.total_seconds() < 0:
            raise ValueError("FrozenClock may only advance forwards")
        self._instant = self._instant + delta
