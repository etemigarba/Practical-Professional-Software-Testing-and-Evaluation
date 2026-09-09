"""Slide 21 — consumer-driven contract testing.

A schema says what *may* be sent; a pact says what this consumer actually
*depends on*, which is what tells you where you are free to change.

**Deviation D3.**  Verification is pure Python and in-process rather than going
through a Pact broker, so the default suite stays network-free.  The real Pact
v3 DSL is preserved in ``examples/js/contract/`` for readers who want it.

Note the third interaction and ``forbiddenFields``: the contract pins the error
shape and the fields that must *never* appear, so an over-sharing response
breaks the provider's build rather than reaching a consumer.
"""

from __future__ import annotations

import json
import random
import re
from pathlib import Path
from typing import Any

import pytest

from stplaybook.invoicing import InvoiceApi, InvoiceRepository
from tests.factories import make_invoice, make_principal

PACT_PATH = Path(__file__).parent / "pacts" / "invoice-consumer-invoice-provider.json"


def _pact() -> dict[str, Any]:
    return json.loads(PACT_PATH.read_text(encoding="utf-8"))


def _interactions() -> list[dict[str, Any]]:
    return _pact()["interactions"]


def _matches(rule: dict[str, Any], value: Any) -> bool:
    if rule["match"] == "regex":
        return re.fullmatch(rule["regex"], str(value)) is not None
    if rule["match"] == "type":
        return {"integer": int, "string": str}[rule["type"]] is type(value)
    raise AssertionError(f"unknown matcher {rule['match']!r}")


def test_the_pact_declares_the_interactions_the_consumer_depends_on() -> None:
    pact = _pact()

    assert pact["consumer"]["name"] == "invoice-consumer"
    assert len(pact["interactions"]) == 3


@pytest.mark.parametrize("interaction", _interactions(), ids=lambda i: i["description"])
def test_provider_satisfies_every_consumer_expectation(
    interaction: dict[str, Any],
    repository: InvoiceRepository,
    api: InvoiceApi,
    rng: random.Random,
) -> None:
    """Replay each recorded expectation against the real provider."""
    invoice = repository.save(make_invoice(rng, tenant="tenant-a", naira=45_000))
    request = interaction["request"]
    path = request["path"].replace("{invoiceId}", invoice.id)

    response = api.request(request["method"], path, principal=make_principal(request["principal"]))

    assert response.status == interaction["response"]["status"]


def test_successful_response_satisfies_every_matching_rule(
    repository: InvoiceRepository, api: InvoiceApi, rng: random.Random
) -> None:
    interaction = _interactions()[0]
    invoice = repository.save(make_invoice(rng, tenant="tenant-a", naira=45_000))

    response = api.request("GET", f"/invoices/{invoice.id}", principal=make_principal("owner"))

    assert response.body is not None
    for pointer, rule in interaction["response"]["matchingRules"].items():
        field = pointer.removeprefix("$.body.")
        assert field in response.body, f"contract requires field {field!r}"
        assert _matches(rule, response.body[field]), f"{field!r} violates {rule}"


def test_response_omits_every_forbidden_field(
    repository: InvoiceRepository, api: InvoiceApi, rng: random.Random
) -> None:
    """A contract test catches an over-sharing response (slide 21)."""
    interaction = _interactions()[0]
    invoice = repository.save(make_invoice(rng, tenant="tenant-a"))

    response = api.request("GET", f"/invoices/{invoice.id}", principal=make_principal("owner"))

    assert response.body is not None
    for forbidden in interaction["response"]["forbiddenFields"]:
        assert forbidden not in response.body


def test_error_interactions_pin_an_empty_body(
    repository: InvoiceRepository, api: InvoiceApi, rng: random.Random
) -> None:
    """The error shape is part of the contract, not an implementation detail."""
    invoice = repository.save(make_invoice(rng, tenant="tenant-a"))

    for interaction in _interactions()[1:]:
        response = api.request(
            interaction["request"]["method"],
            f"/invoices/{invoice.id}",
            principal=make_principal(interaction["request"]["principal"]),
        )
        assert response.body is None
        assert response.status == interaction["response"]["status"]
