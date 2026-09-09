"""Configuration read from the environment and validated at boot.

Slide 24: model names, API keys and environment-specific values never appear in
source.  Everything opt-in in this repository is switched here, and an
unparseable value fails loudly at start-up rather than halfway through a suite.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from .errors import ConfigurationError

__all__ = ["Settings"]

_TRUE = frozenset({"1", "true", "yes", "on"})
_FALSE = frozenset({"0", "false", "no", "off", ""})


def _flag(name: str, env: dict[str, str]) -> bool:
    raw = env.get(name, "").strip().lower()
    if raw in _TRUE:
        return True
    if raw in _FALSE:
        return False
    raise ConfigurationError(name, "expected a boolean such as 1/0 or true/false")


def _positive_int(name: str, env: dict[str, str], default: int) -> int:
    raw = env.get(name, "").strip()
    if not raw:
        return default
    if not raw.isdigit() or int(raw) <= 0:
        raise ConfigurationError(name, "expected a positive integer")
    return int(raw)


@dataclass(frozen=True)
class Settings:
    """Every switch this repository honours. All default to off."""

    use_postgres: bool = False
    enable_fuzz: bool = False
    postgres_image: str = "postgres:17-alpine"
    fuzz_seconds: int = 30
    diff_coverage_floor: int = 80
    mutation_score_floor: int = 70

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> Settings:
        """Build settings, raising :class:`ConfigurationError` on bad input."""
        source = dict(os.environ if env is None else env)
        image = source.get("STP_POSTGRES_IMAGE", "postgres:17-alpine").strip()
        if image.endswith(":latest"):
            raise ConfigurationError(
                "STP_POSTGRES_IMAGE", "pin an explicit tag; ':latest' is not reproducible"
            )
        return cls(
            use_postgres=_flag("STP_USE_POSTGRES", source),
            enable_fuzz=_flag("STP_ENABLE_FUZZ", source),
            postgres_image=image or "postgres:17-alpine",
            fuzz_seconds=_positive_int("STP_FUZZ_SECONDS", source, 30),
            diff_coverage_floor=_positive_int("STP_DIFF_COVERAGE_FLOOR", source, 80),
            mutation_score_floor=_positive_int("STP_MUTATION_SCORE_FLOOR", source, 70),
        )
