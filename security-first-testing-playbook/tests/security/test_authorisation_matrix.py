"""Slide 33 — the tests no scanner can write for you.

Broken access control has stayed at the top of the OWASP list because it is
application-specific: nothing can derive who *should* be permitted to do what.
This is the matrix, enumerated rather than sampled.

**Correction to slide 33.**  The slide asserts ``status in (401, 404)`` for every
denial, which would pass even if an anonymous caller received a
resource-confirming 404.  Denials are pinned exactly, per principal.
"""

from __future__ import annotations

import random

import pytest

from stplaybook.authz import MatrixCase, enumerate_matrix
from stplaybook.invoicing import InvoiceApi, InvoiceRepository
from tests.factories import make_invoice, make_principal

MATRIX = enumerate_matrix()


def test_the_matrix_is_exhaustive_not_sampled() -> None:
    """Four principals times three operations. Adding either grows this."""
    assert len(MATRIX) == 12
    assert len({(c.principal, c.operation) for c in MATRIX}) == 12


@pytest.mark.parametrize("case", MATRIX, ids=lambda c: c.id)
def test_invoice_authorisation_matrix(
    case: MatrixCase, repository: InvoiceRepository, api: InvoiceApi, rng: random.Random
) -> None:
    invoice = repository.save(make_invoice(rng, tenant="tenant-a"))
    principal = make_principal(case.principal)

    response = api.request(case.operation, f"/invoices/{invoice.id}", principal=principal)

    assert response.status == case.expectation.status


@pytest.mark.parametrize(
    "case", [c for c in MATRIX if not c.expectation.permitted], ids=lambda c: c.id
)
def test_denied_responses_never_disclose_the_resource(
    case: MatrixCase, repository: InvoiceRepository, api: InvoiceApi, rng: random.Random
) -> None:
    """Assert on what is *not* returned — where disclosure bugs are caught."""
    invoice = repository.save(make_invoice(rng, tenant="tenant-a"))
    principal = make_principal(case.principal)

    response = api.request(case.operation, f"/invoices/{invoice.id}", principal=principal)

    assert invoice.id not in response.text
    assert response.body is None


def test_an_admin_of_another_tenant_holds_no_authority_here(
    repository: InvoiceRepository, api: InvoiceApi, rng: random.Random
) -> None:
    """Role is not authority; tenancy is."""
    invoice = repository.save(make_invoice(rng, tenant="tenant-a"))

    response = api.request(
        "DELETE", f"/invoices/{invoice.id}", principal=make_principal("other_tenant_admin")
    )

    assert response.status == 404
    assert repository.find_all(tenant="tenant-a") != []
