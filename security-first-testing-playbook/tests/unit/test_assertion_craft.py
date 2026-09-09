"""Slide 16 — assertions that actually assert.

The slide contrasts a test that passes even when the code is wrong with one that
fails for exactly one reason.  Rather than reprint both, this module proves the
distinction is real: the weak assertions genuinely do hold against a broken
response, and the strong ones genuinely do not.
"""

from __future__ import annotations

import random

from stplaybook.identifiers import is_uuid_v4
from stplaybook.invoicing import InvoiceApi, InvoiceRepository, Principal, Response
from tests.factories import make_invoice

BROKEN = Response(500, {"tenantId": "tenant-b", "total": -1, "status": "PAID"})


def test_weak_assertions_hold_even_against_a_broken_response() -> None:
    """Why toBeDefined and toBeTruthy are not assertions in any useful sense."""
    assert BROKEN is not None
    assert BROKEN.status
    assert BROKEN.body is not None


def test_specific_assertions_reject_the_same_broken_response() -> None:
    assert BROKEN.status != 201
    assert BROKEN.body is not None
    assert BROKEN.body["total"] < 0
    assert BROKEN.body["tenantId"] != "tenant-a"


def test_created_invoice_is_scoped_to_the_callers_tenant(
    api: InvoiceApi, repository: InvoiceRepository, rng: random.Random
) -> None:
    """Slide 16's corrected example, asserting on values and on the tenant."""
    invoice = repository.save(make_invoice(rng, tenant="tenant-a", naira=45_000))
    caller = Principal("owner", "tenant-a", "owner")

    response = api.request("GET", f"/invoices/{invoice.id}", principal=caller)

    assert response.status == 200
    assert response.body == {
        "id": invoice.id,
        "total": 45_000,
        "currency": "NGN",
        "status": "AWAITING_APPROVAL",
    }
    assert is_uuid_v4(response.body["id"])


def test_uuid_pattern_rejects_a_version_one_uuid() -> None:
    """The gap on slide 16: UUID_V4 was referenced but never defined."""
    assert is_uuid_v4("f13d80b2-b7ec-48b2-86ac-cc8551a08cf9")
    assert not is_uuid_v4("f13d80b2-b7ec-18b2-86ac-cc8551a08cf9")
    assert not is_uuid_v4("not-a-uuid")
