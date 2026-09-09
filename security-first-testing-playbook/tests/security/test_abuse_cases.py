"""Slide 29 — from STRIDE threat to executable test.

Each test below names the threat it derives from.  The rule the slide states is
observed here: every test was first seen to fail against a vulnerable version,
so none of them is an assumption dressed as a control.
"""

from __future__ import annotations

import random

import pytest

from stplaybook.errors import InvoiceNotFound, TenantMismatch
from stplaybook.invoicing import ANONYMOUS, InvoiceApi, InvoiceRepository
from tests.factories import make_invoice, make_principal


def test_elevation_of_privilege_guessed_identifier_returns_404_not_403(
    repository: InvoiceRepository, api: InvoiceApi, rng: random.Random
) -> None:
    """STRIDE: Elevation of privilege. A 403 with a body confirms existence."""
    invoice = repository.save(make_invoice(rng, tenant="tenant-a"))

    response = api.request(
        "GET", f"/invoices/{invoice.id}", principal=make_principal("other_tenant_admin")
    )

    assert response.status == 404
    assert response.status != 403


def test_information_disclosure_repository_error_names_no_internals(
    repository: InvoiceRepository, rng: random.Random
) -> None:
    """STRIDE: Information disclosure. Error text must not leak structure."""
    invoice = repository.save(make_invoice(rng, tenant="tenant-a"))

    with pytest.raises(TenantMismatch) as err:
        repository.load(invoice.id, tenant="tenant-b")

    message = str(err.value)
    assert "tenant-b" in message
    assert "SELECT" not in message.upper()
    assert "postgres" not in message.lower()


def test_spoofing_an_unauthenticated_caller_is_stopped_before_any_read(
    repository: InvoiceRepository, api: InvoiceApi, rng: random.Random
) -> None:
    """STRIDE: Spoofing. Authorisation precedes the lookup, not the reverse."""
    invoice = repository.save(make_invoice(rng, tenant="tenant-a"))

    response = api.request("DELETE", f"/invoices/{invoice.id}", principal=ANONYMOUS)

    assert response.status == 401
    assert repository.load(invoice.id, tenant="tenant-a") == invoice


def test_tampering_deleting_another_tenants_invoice_changes_nothing(
    repository: InvoiceRepository, api: InvoiceApi, rng: random.Random
) -> None:
    """STRIDE: Tampering. A denial must have no side effect."""
    invoice = repository.save(make_invoice(rng, tenant="tenant-a"))

    api.request("DELETE", f"/invoices/{invoice.id}", principal=make_principal("other_tenant_admin"))

    assert repository.load(invoice.id, tenant="tenant-a") == invoice


def test_missing_and_forbidden_are_indistinguishable_at_the_boundary(
    repository: InvoiceRepository, api: InvoiceApi, rng: random.Random
) -> None:
    """Both render 404: the distinction is the disclosure."""
    invoice = repository.save(make_invoice(rng, tenant="tenant-a"))
    outsider = make_principal("other_tenant_admin")

    forbidden = api.request("GET", f"/invoices/{invoice.id}", principal=outsider)
    missing = api.request("GET", "/invoices/does-not-exist", principal=outsider)

    assert forbidden.status == missing.status == 404
    assert forbidden.body == missing.body is None


def test_repository_raises_distinct_errors_internally(
    repository: InvoiceRepository, rng: random.Random
) -> None:
    """Internally the two cases differ; only the boundary collapses them."""
    invoice = repository.save(make_invoice(rng, tenant="tenant-a"))

    with pytest.raises(InvoiceNotFound):
        repository.load("no-such-id", tenant="tenant-a")
    with pytest.raises(TenantMismatch):
        repository.load(invoice.id, tenant="tenant-b")
