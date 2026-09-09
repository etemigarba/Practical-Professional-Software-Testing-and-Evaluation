"""The invoice service the deck keeps referring to.

Slides 16, 29 and 33 all assert against an invoice API that is never defined.
This module is that API.  It is the single subject shared by the contract tests,
the abuse-case tests and the authorisation-matrix test, so those three suites
verify one system rather than three imagined ones.

Two security decisions are load-bearing:

* an unauthorised-but-authenticated caller receives **404, not 403** — a 403
  with a body confirms the resource exists, which is itself a disclosure;
* an anonymous caller receives **401**, distinguishable from the above, because
  "you must authenticate" and "this does not exist for you" are different facts.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, replace
from typing import Any, Literal

from .errors import InvoiceNotFound, TenantMismatch
from .identifiers import new_id
from .money import Naira

__all__ = ["ANONYMOUS", "Invoice", "InvoiceApi", "InvoiceRepository", "Principal", "Response"]

InvoiceStatus = Literal["DRAFT", "AWAITING_APPROVAL", "PAID"]


@dataclass(frozen=True)
class Invoice:
    """An invoice belonging to exactly one tenant."""

    id: str
    tenant: str
    total: Naira
    status: InvoiceStatus = "AWAITING_APPROVAL"
    currency: str = "NGN"

    def to_body(self) -> dict[str, Any]:
        """Serialise for the API boundary. Tenant is never exposed to callers."""
        return {
            "id": self.id,
            "total": self.total.to_naira_int(),
            "currency": self.currency,
            "status": self.status,
        }


@dataclass(frozen=True)
class Principal:
    """Whoever is making the request."""

    name: str
    tenant: str | None
    role: Literal["owner", "viewer", "admin", "anonymous"]

    @property
    def is_authenticated(self) -> bool:
        return self.role != "anonymous"


ANONYMOUS = Principal(name="anonymous", tenant=None, role="anonymous")


class InvoiceRepository:
    """In-memory, tenant-scoped storage.

    Every read takes a tenant.  There is no API through which a caller can ask
    for an invoice without saying who they are asking as — the isolation is
    structural rather than a check somebody might forget to write.
    """

    def __init__(self) -> None:
        self._rows: dict[str, Invoice] = {}

    def save(self, invoice: Invoice) -> Invoice:
        """Persist and return the stored invoice, assigning an id if absent."""
        stored = invoice if invoice.id else replace(invoice, id=new_id())
        self._rows[stored.id] = stored
        return stored

    def find_all(self, *, tenant: str) -> list[Invoice]:
        """Every invoice visible to ``tenant``, oldest first."""
        return [row for row in self._rows.values() if row.tenant == tenant]

    def load(self, invoice_id: str, *, tenant: str) -> Invoice:
        """Load one invoice, or raise.

        Raises :class:`InvoiceNotFound` when nothing exists and
        :class:`TenantMismatch` when it exists for somebody else.  Callers at the
        API boundary must render both as 404.
        """
        row = self._rows.get(invoice_id)
        if row is None:
            raise InvoiceNotFound(invoice_id)
        if row.tenant != tenant:
            raise TenantMismatch(invoice_id, tenant)
        return row

    def delete(self, invoice_id: str, *, tenant: str) -> None:
        """Remove one invoice, enforcing the same scoping as :meth:`load`."""
        self.load(invoice_id, tenant=tenant)
        del self._rows[invoice_id]


@dataclass(frozen=True)
class Response:
    """An API response. ``text`` exists so tests can assert on absence."""

    status: int
    body: dict[str, Any] | None = None

    @property
    def text(self) -> str:
        return "" if self.body is None else repr(self.body)


class InvoiceApi:
    """A minimal in-process router over :class:`InvoiceRepository`."""

    def __init__(self, repository: InvoiceRepository) -> None:
        self._repository = repository

    def request(self, method: str, path: str, *, principal: Principal) -> Response:
        """Route one request. Authorisation is decided before anything is read."""
        if not principal.is_authenticated:
            return Response(401)
        if not path.startswith("/invoices/"):
            return Response(404)

        invoice_id = path.removeprefix("/invoices/")
        tenant = principal.tenant or ""

        try:
            invoice = self._repository.load(invoice_id, tenant=tenant)
        except (InvoiceNotFound, TenantMismatch):
            return Response(404)

        if method == "GET":
            return Response(200, invoice.to_body())
        if method == "PATCH":
            if principal.role == "viewer":
                return Response(404)
            updated = self._repository.save(replace(invoice, status="PAID"))
            return Response(200, updated.to_body())
        if method == "DELETE":
            if principal.role != "owner":
                return Response(404)
            self._repository.delete(invoice_id, tenant=tenant)
            return Response(204)
        return Response(405)


def synthetic_invoice(tenant: str, rng: random.Random) -> Invoice:
    """Build a synthetic invoice. No production data ever enters a fixture."""
    return Invoice(
        id=new_id(),
        tenant=tenant,
        total=Naira(rng.randrange(1_000, 500_000)),
    )
