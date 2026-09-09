"""VEX: which advertised CVEs actually matter here.

Slide 35: a VEX statement is a producer assertion that a CVE flagged against a
component in the SBOM is, or is not, exploitable in *this* product.  It is what
stops a 400-finding scanner report becoming a 400-ticket backlog.

The status vocabulary follows CSAF VEX.  ``not_affected`` requires a
justification -- an unjustified refutation is an opinion, and this module
refuses to apply one.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from ..errors import SbomError
from .triage import Finding

__all__ = ["VexStatement", "VexStatus", "apply_vex", "load_vex", "parse_vex"]


class VexStatus(StrEnum):
    """CSAF VEX product status."""

    NOT_AFFECTED = "not_affected"
    AFFECTED = "affected"
    FIXED = "fixed"
    UNDER_INVESTIGATION = "under_investigation"


@dataclass(frozen=True)
class VexStatement:
    """One producer assertion about one CVE in one product."""

    cve: str
    product: str
    status: VexStatus
    justification: str | None = None

    @property
    def refutes(self) -> bool:
        """Only a *justified* not_affected refutes a finding."""
        return self.status is VexStatus.NOT_AFFECTED and bool(self.justification)


def parse_vex(document: str) -> tuple[VexStatement, ...]:
    """Parse a simplified CSAF VEX document, or raise :class:`SbomError`."""
    try:
        raw = json.loads(document)
    except json.JSONDecodeError as exc:
        raise SbomError(f"VEX is not valid JSON ({exc.msg})") from exc
    if not isinstance(raw, dict) or "vulnerabilities" not in raw:
        raise SbomError("VEX document needs a 'vulnerabilities' array")

    statements: list[VexStatement] = []
    for vuln in raw["vulnerabilities"]:
        cve = vuln.get("cve")
        if not cve:
            raise SbomError("every VEX vulnerability needs a 'cve'")
        for status_name, products in (vuln.get("product_status") or {}).items():
            try:
                status = VexStatus(status_name)
            except ValueError as exc:
                raise SbomError(f"unknown VEX status {status_name!r}") from exc
            for product in products:
                statements.append(
                    VexStatement(
                        cve=cve,
                        product=product,
                        status=status,
                        justification=vuln.get("justification"),
                    )
                )
    return tuple(statements)


def load_vex(path: Path) -> tuple[VexStatement, ...]:
    """Read and parse a VEX document from disk."""
    return parse_vex(path.read_text(encoding="utf-8"))


def apply_vex(
    findings: list[Finding], statements: tuple[VexStatement, ...], *, product: str
) -> list[Finding]:
    """Mark findings refuted by a justified ``not_affected`` for this product.

    Findings are annotated, never deleted.  A suppressed finding that leaves no
    trace is indistinguishable from one nobody ever looked at.
    """
    from dataclasses import replace

    refuted = {s.cve for s in statements if s.product == product and s.refutes}
    return [replace(f, vex_refuted=True) if f.cve in refuted else f for f in findings]
