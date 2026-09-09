"""Slide 24 — configuration validated at boot, never hardcoded."""

from __future__ import annotations

import pytest

from stplaybook.config import Settings
from stplaybook.errors import ConfigurationError


def test_everything_defaults_to_off() -> None:
    settings = Settings.from_env({})

    assert settings.use_postgres is False
    assert settings.enable_fuzz is False
    assert settings.diff_coverage_floor == 80


def test_flags_are_parsed_from_the_environment() -> None:
    settings = Settings.from_env({"STP_USE_POSTGRES": "1", "STP_ENABLE_FUZZ": "true"})

    assert settings.use_postgres is True
    assert settings.enable_fuzz is True


def test_a_non_boolean_flag_fails_loudly_at_boot() -> None:
    with pytest.raises(ConfigurationError) as err:
        Settings.from_env({"STP_USE_POSTGRES": "maybe"})
    assert err.value.variable == "STP_USE_POSTGRES"


def test_a_latest_image_tag_is_refused_as_irreproducible() -> None:
    with pytest.raises(ConfigurationError) as err:
        Settings.from_env({"STP_POSTGRES_IMAGE": "postgres:latest"})
    assert "not reproducible" in err.value.reason


def test_a_negative_threshold_is_refused() -> None:
    with pytest.raises(ConfigurationError) as err:
        Settings.from_env({"STP_DIFF_COVERAGE_FLOOR": "-5"})
    assert err.value.variable == "STP_DIFF_COVERAGE_FLOOR"
