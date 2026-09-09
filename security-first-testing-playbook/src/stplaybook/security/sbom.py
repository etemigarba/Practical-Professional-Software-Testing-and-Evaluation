"""Minimal CycloneDX reader.

Slide 35: the SBOM answers *what is inside*.  Generate it at build time, when
the dependency graph is fully resolved -- a manifest read at development time
records intent, not what shipped.

Deliberately dependency-free: parsing a JSON document to answer "which
components are in this build?" does not warrant adding a library to a repository
whose whole argument is that every dependency is a component you must trust.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..errors import SbomError

__all__ = ["Component", "Sbom", "load_sbom", "parse_sbom"]


@dataclass(frozen=True)
class Component:
    """One component recorded in the bill of materials."""

    name: str
    version: str
    purl: str | None = None
    licences: tuple[str, ...] = ()

    @property
    def coordinate(self) -> str:
        return f"{self.name}@{self.version}"


@dataclass(frozen=True)
class Sbom:
    """A parsed CycloneDX bill of materials."""

    spec_version: str
    serial_number: str | None
    components: tuple[Component, ...]

    def find(self, name: str) -> Component | None:
        """Return the component with this name, if present."""
        return next((c for c in self.components if c.name == name), None)

    def coordinates(self) -> frozenset[str]:
        """Every ``name@version`` in the document."""
        return frozenset(c.coordinate for c in self.components)

    def forbidden_licences(self, disallowed: frozenset[str]) -> tuple[Component, ...]:
        """Components carrying a licence the policy forbids."""
        return tuple(c for c in self.components if any(lic in disallowed for lic in c.licences))


def _licences_of(raw: dict[str, Any]) -> tuple[str, ...]:
    found: list[str] = []
    for entry in raw.get("licenses", []) or []:
        if not isinstance(entry, dict):
            continue
        if isinstance(entry.get("license"), dict):
            identifier = entry["license"].get("id") or entry["license"].get("name")
            if identifier:
                found.append(str(identifier))
        elif entry.get("expression"):
            found.append(str(entry["expression"]))
    return tuple(found)


def parse_sbom(document: str) -> Sbom:
    """Parse a CycloneDX JSON document, or raise :class:`SbomError`."""
    try:
        raw = json.loads(document)
    except json.JSONDecodeError as exc:
        raise SbomError(f"not valid JSON ({exc.msg})") from exc
    if not isinstance(raw, dict):
        raise SbomError("top level must be an object")
    if raw.get("bomFormat") != "CycloneDX":
        raise SbomError("bomFormat must be 'CycloneDX'")
    spec_version = raw.get("specVersion")
    if not isinstance(spec_version, str):
        raise SbomError("specVersion is missing")

    components: list[Component] = []
    for entry in raw.get("components", []) or []:
        if not isinstance(entry, dict):
            raise SbomError("every component must be an object")
        name, version = entry.get("name"), entry.get("version")
        if not name or not version:
            raise SbomError("every component needs a name and a version")
        components.append(
            Component(
                name=str(name),
                version=str(version),
                purl=entry.get("purl"),
                licences=_licences_of(entry),
            )
        )
    return Sbom(
        spec_version=spec_version,
        serial_number=raw.get("serialNumber"),
        components=tuple(components),
    )


def load_sbom(path: Path) -> Sbom:
    """Read and parse an SBOM from disk."""
    return parse_sbom(path.read_text(encoding="utf-8"))
