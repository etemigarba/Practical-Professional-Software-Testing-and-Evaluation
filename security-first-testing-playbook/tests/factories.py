"""Synthetic data factories.

Slide 24 is unambiguous: never copy personal data into a test environment.  Under
the Nigeria Data Protection Act 2023 and the NDPC's 2025 directive, a production
dump in staging is a processing activity requiring a lawful basis and a record.
Everything below is generated, and no value here corresponds to a real person,
account or business.
"""

from __future__ import annotations

import random

from stplaybook.identifiers import new_id
from stplaybook.invoicing import Invoice, Principal
from stplaybook.money import Naira
from stplaybook.nuban import generate_nuban
from stplaybook.security.triage import Finding

__all__ = [
    "make_account_number",
    "make_finding",
    "make_invoice",
    "make_principal",
    "make_statement_bytes",
]

_TEST_BANK_CODE = "058"


def make_account_number(rng: random.Random) -> str:
    """A structurally valid but entirely fictional NUBAN."""
    return generate_nuban(_TEST_BANK_CODE, rng)


def make_invoice(
    rng: random.Random, *, tenant: str = "tenant-a", naira: int | None = None
) -> Invoice:
    """An invoice with a whole-naira total, so the API boundary can render it."""
    amount = naira if naira is not None else rng.randrange(1_000, 500_000)
    return Invoice(id=new_id(), tenant=tenant, total=Naira(amount))


def make_principal(name: str) -> Principal:
    """Map a matrix principal name onto a concrete caller."""
    return {
        "owner": Principal("owner", "tenant-a", "owner"),
        "same_tenant_viewer": Principal("viewer", "tenant-a", "viewer"),
        "other_tenant_admin": Principal("outsider", "tenant-b", "admin"),
        "anonymous": Principal("anonymous", None, "anonymous"),
    }[name]


def make_finding(cve: str, **overrides: object) -> Finding:
    """A vulnerability finding with sensible, overridable defaults."""
    defaults: dict[str, object] = {
        "component": "libexample",
        "cvss": 5.0,
        "epss": 0.01,
    }
    defaults.update(overrides)
    return Finding(cve=cve, **defaults)  # type: ignore[arg-type]


def make_statement_bytes(rng: random.Random, *, lines: int = 3) -> bytes:
    """A well-formed statement, used to seed the fuzzing corpus."""
    account = make_account_number(rng)
    amounts = [rng.randrange(100, 5_000_000) for _ in range(lines)]
    rows = [f"H|NGN|{account}"]
    rows += [f"L|line {i}|{amount}" for i, amount in enumerate(amounts)]
    rows.append(f"T|{sum(amounts)}")
    return "\n".join(rows).encode("utf-8")
