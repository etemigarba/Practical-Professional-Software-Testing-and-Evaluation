"""Shared fixtures.

Two rules hold across every suite:

* **no shared state** — each test builds its own tenant, account and invoice;
* **no ambient time or randomness** — the clock is frozen and the RNG is seeded,
  so a test that passes in Abuja in September passes in Lagos in January.
"""

from __future__ import annotations

import random
from datetime import UTC, datetime
from pathlib import Path

import pytest

from stplaybook.clock import FrozenClock
from stplaybook.config import Settings
from stplaybook.invoicing import InvoiceApi, InvoiceRepository
from stplaybook.ledger import Account
from stplaybook.money import Naira

REPO_ROOT = Path(__file__).resolve().parents[1]
GOLDEN = Path(__file__).parent / "golden"


@pytest.fixture
def settings() -> Settings:
    """Settings read from a controlled environment, never the real one."""
    return Settings.from_env({})


@pytest.fixture
def clock() -> FrozenClock:
    """A clock frozen at a fixed instant, advanceable within a test."""
    return FrozenClock(datetime(2026, 9, 7, 9, 0, tzinfo=UTC))


@pytest.fixture
def rng() -> random.Random:
    """A seeded generator, so synthetic data is reproducible."""
    return random.Random(20260907)


@pytest.fixture
def account(clock: FrozenClock) -> Account:
    """The account from slide 15: ₦500,000 balance, ₦200,000 daily limit."""
    return Account(
        balance=Naira(500_000),
        daily_limit=Naira(200_000),
        tenant="tenant-a",
        clock=clock,
    )


@pytest.fixture
def repository() -> InvoiceRepository:
    """A repository containing nothing until the test puts something in it."""
    return InvoiceRepository()


@pytest.fixture
def api(repository: InvoiceRepository) -> InvoiceApi:
    """The invoice API under test."""
    return InvoiceApi(repository)


@pytest.fixture
def golden() -> Path:
    """Directory holding the SBOM, VEX and provenance fixtures."""
    return GOLDEN


@pytest.fixture
def repo_root() -> Path:
    """Repository root, for the self-referential audit test."""
    return REPO_ROOT


@pytest.fixture
def sample_latencies() -> list[float]:
    """A synthetic latency distribution shaped like slide 40's chart."""
    generator = random.Random(40)
    body = [generator.gauss(45, 18) for _ in range(900)]
    tail = [generator.gauss(700, 300) for _ in range(100)]
    return [max(1.0, value) for value in body + tail]
