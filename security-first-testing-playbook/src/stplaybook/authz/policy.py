"""The authorisation policy the matrix test enumerates.

Slide 32 makes the central claim: no scanner finds broken access control,
because no scanner knows who *should* be allowed to do what.  That knowledge
lives here, as data, so it can be enumerated, diffed and reviewed.

**Correction to slide 33.**  The slide asserts ``status_code in (401, 404)`` for
every denied case.  That single assertion accepts a 401 where a 404 is required
and vice versa, so it would pass even if an anonymous caller received a
resource-confirming 404, or an authenticated outsider received a 401 that
reveals the resource exists elsewhere.  Denials are pinned exactly here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal

__all__ = ["DEFAULT_POLICY", "DENIED_STATUS", "Operation", "Policy", "PrincipalName"]

PrincipalName = Literal["owner", "same_tenant_viewer", "other_tenant_admin", "anonymous"]
Operation = Literal["GET", "PATCH", "DELETE"]

SUCCESS_STATUS: Final[dict[Operation, int]] = {"GET": 200, "PATCH": 200, "DELETE": 204}

DENIED_STATUS: Final[dict[PrincipalName, int]] = {
    "anonymous": 401,
    "same_tenant_viewer": 404,
    "other_tenant_admin": 404,
    "owner": 404,
}
"""The exact status a denial must produce, per principal.

``401`` for an unauthenticated caller: "identify yourself" discloses nothing.
``404`` for everyone else: a ``403`` with a body confirms the resource exists,
which is the disclosure the control exists to prevent.
"""


@dataclass(frozen=True)
class Policy:
    """Which principal may perform which operation."""

    allowed: frozenset[tuple[PrincipalName, Operation]]

    def permits(self, principal: PrincipalName, operation: Operation) -> bool:
        """Return ``True`` when this exact pair is permitted."""
        return (principal, operation) in self.allowed

    def expected_status(self, principal: PrincipalName, operation: Operation) -> int:
        """The one status this pair must produce. Never a range."""
        if self.permits(principal, operation):
            return SUCCESS_STATUS[operation]
        return DENIED_STATUS[principal]


DEFAULT_POLICY: Final = Policy(
    allowed=frozenset(
        {
            ("owner", "GET"),
            ("owner", "PATCH"),
            ("owner", "DELETE"),
            ("same_tenant_viewer", "GET"),
        }
    )
)
"""The invoice policy used throughout the repository.

Note what is absent: ``other_tenant_admin`` holds an admin role and still
appears nowhere.  Role is not authority; tenancy is.
"""
