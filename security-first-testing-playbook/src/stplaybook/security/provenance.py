"""Offline verification of build provenance.

Slide 35: SLSA answers *how it was built*, Sigstore answers *who vouches for
it*.  Verification belongs at **deploy** time, not merely at publish time --
verifying only at publish leaves the window between publish and deploy
unguarded, which is the window slide 29's tampering abuse case describes.

This verifier is fully offline: it checks a digest, a builder allow-list, and a
source repository, all against material already in hand.  No signature
cryptography and no transparency-log lookup, both of which would require network
access; ``docs/security.md`` records that boundary explicitly.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from ..errors import ProvenanceRejected

__all__ = ["ProvenanceCheck", "parse_provenance", "sha256_of", "verify_provenance"]


@dataclass(frozen=True)
class ProvenanceCheck:
    """The outcome of verifying one artefact against one attestation."""

    artefact: str
    verified: bool
    builder_id: str
    source_uri: str
    reasons: tuple[str, ...] = ()

    def describe(self) -> str:
        if self.verified:
            return f"{self.artefact}: provenance verified (built by {self.builder_id})"
        return f"{self.artefact}: REJECTED -- " + "; ".join(self.reasons)


def sha256_of(data: bytes) -> str:
    """Hex SHA-256 digest of ``data``."""
    return hashlib.sha256(data).hexdigest()


def parse_provenance(document: str) -> dict[str, Any]:
    """Parse an in-toto statement, or raise :class:`ProvenanceRejected`."""
    try:
        raw = json.loads(document)
    except json.JSONDecodeError as exc:
        raise ProvenanceRejected(f"attestation is not valid JSON ({exc.msg})") from exc
    if not isinstance(raw, dict):
        raise ProvenanceRejected("attestation must be a JSON object")
    if raw.get("_type") != "https://in-toto.io/Statement/v1":
        raise ProvenanceRejected("not an in-toto v1 statement")
    if not raw.get("subject"):
        raise ProvenanceRejected("attestation names no subject")
    return raw


def verify_provenance(
    *,
    artefact_bytes: bytes,
    artefact_name: str,
    attestation: str,
    trusted_builders: frozenset[str],
    expected_source: str,
) -> ProvenanceCheck:
    """Verify an artefact against its attestation.

    **Fails closed.**  Every deviation is collected and the artefact is rejected
    if any is present; an unverifiable artefact is never treated as acceptable,
    which is the whole point of the deploy-time gate on slide 36.
    """
    statement = parse_provenance(attestation)
    predicate = statement.get("predicate") or {}
    builder_id = str((predicate.get("runDetails") or {}).get("builder", {}).get("id", ""))
    source_uri = str(
        (predicate.get("buildDefinition") or {}).get("externalParameters", {}).get("source", "")
    )

    reasons: list[str] = []

    subject = next((s for s in statement["subject"] if s.get("name") == artefact_name), None)
    if subject is None:
        reasons.append(f"attestation does not cover artefact {artefact_name!r}")
    else:
        declared = str((subject.get("digest") or {}).get("sha256", ""))
        actual = sha256_of(artefact_bytes)
        if declared != actual:
            reasons.append(f"digest mismatch (declared {declared[:12]}…, actual {actual[:12]}…)")

    if not builder_id:
        reasons.append("attestation names no builder")
    elif builder_id not in trusted_builders:
        reasons.append(f"builder {builder_id!r} is not in the trusted set")

    if source_uri != expected_source:
        reasons.append(f"source {source_uri!r} does not match expected {expected_source!r}")

    return ProvenanceCheck(
        artefact=artefact_name,
        verified=not reasons,
        builder_id=builder_id,
        source_uri=source_uri,
        reasons=tuple(reasons),
    )
