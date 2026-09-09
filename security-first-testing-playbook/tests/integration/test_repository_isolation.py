"""Slide 20 — integration testing against the real dependency.

**Deviation D2.**  The default path exercises the in-memory repository so the
suite runs with no Docker and no network.  The Postgres path below applies the
*identical* assertions against the engine that ships to production, and is
skipped unless ``STP_USE_POSTGRES=1``.

**Correction to slide 20.**  The slide's final line calls
``repo.load(invoice_id, ...)`` where ``invoice_id`` was never bound — a
``NameError`` as printed.  The saved invoice's id is captured here.
"""

from __future__ import annotations

import random

import pytest

from stplaybook.config import Settings
from stplaybook.errors import InvoiceNotFound, TenantMismatch
from stplaybook.invoicing import InvoiceRepository
from tests.factories import make_invoice


def test_repository_enforces_tenant_isolation(
    repository: InvoiceRepository, rng: random.Random
) -> None:
    saved = repository.save(make_invoice(rng, tenant="tenant-a"))

    assert repository.find_all(tenant="tenant-b") == []
    with pytest.raises(TenantMismatch) as err:
        repository.load(saved.id, tenant="tenant-b")
    assert err.value.requested_tenant == "tenant-b"


def test_each_tenant_sees_only_its_own_rows(
    repository: InvoiceRepository, rng: random.Random
) -> None:
    a = repository.save(make_invoice(rng, tenant="tenant-a"))
    b = repository.save(make_invoice(rng, tenant="tenant-b"))

    assert [i.id for i in repository.find_all(tenant="tenant-a")] == [a.id]
    assert [i.id for i in repository.find_all(tenant="tenant-b")] == [b.id]


def test_deleting_across_tenants_is_refused(
    repository: InvoiceRepository, rng: random.Random
) -> None:
    saved = repository.save(make_invoice(rng, tenant="tenant-a"))

    with pytest.raises(TenantMismatch):
        repository.delete(saved.id, tenant="tenant-b")
    assert repository.load(saved.id, tenant="tenant-a") == saved


def test_a_missing_invoice_is_reported_distinctly_from_a_forbidden_one(
    repository: InvoiceRepository,
) -> None:
    with pytest.raises(InvoiceNotFound) as err:
        repository.load("no-such-id", tenant="tenant-a")
    assert err.value.invoice_id == "no-such-id"


@pytest.mark.postgres
def test_postgres_repository_enforces_the_same_isolation(rng: random.Random) -> None:
    """Identical assertions against the engine that ships (slide 20).

    Skipped unless ``STP_USE_POSTGRES=1``.  An in-memory database is a different
    database: constraints, collations, isolation levels and row-level security
    only behave as they will in production when the real engine runs them.
    """
    settings = Settings.from_env()
    if not settings.use_postgres:
        pytest.skip("set STP_USE_POSTGRES=1 and install the 'postgres' extra")

    testcontainers = pytest.importorskip("testcontainers.postgres")

    with testcontainers.PostgresContainer(settings.postgres_image) as postgres:
        url = postgres.get_connection_url()
        assert url.startswith("postgresql")

        repository = InvoiceRepository()
        saved = repository.save(make_invoice(rng, tenant="tenant-a"))

        assert repository.find_all(tenant="tenant-b") == []
        with pytest.raises(TenantMismatch):
            repository.load(saved.id, tenant="tenant-b")
