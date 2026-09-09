"""Slide 40 — percentiles, and why the mean lies."""

from __future__ import annotations

import pytest

from stplaybook.errors import ThresholdSyntaxError
from stplaybook.slo import evaluate_thresholds, parse_threshold, percentile


def test_nearest_rank_percentile_returns_an_observed_sample() -> None:
    samples = [float(n) for n in range(1, 101)]

    assert percentile(samples, 50) == 50.0
    assert percentile(samples, 95) == 95.0
    assert percentile(samples, 99) == 99.0


def test_the_mean_hides_a_tail_the_percentiles_expose(
    sample_latencies: list[float],
) -> None:
    mean = sum(sample_latencies) / len(sample_latencies)

    assert percentile(sample_latencies, 99) > mean * 3


def test_threshold_expression_is_parsed_into_metric_operator_and_value() -> None:
    threshold = parse_threshold("p(95)<250")

    assert threshold.metric == "p(95)"
    assert threshold.operator == "<"
    assert threshold.value == 250.0


def test_unparseable_threshold_is_rejected_by_name() -> None:
    with pytest.raises(ThresholdSyntaxError) as err:
        parse_threshold("p95 is fine")
    assert err.value.expression == "p95 is fine"


def test_thresholds_are_evaluated_independently() -> None:
    samples = [float(n) for n in range(1, 101)]

    results = evaluate_thresholds(samples, ["p(95)<250", "p(95)<10"])

    assert [r.passed for r in results] == [True, False]


def test_a_threshold_with_no_samples_fails_rather_than_passing_vacuously() -> None:
    """Slide 40's `checks: rate>0.99` with no check() calls is exactly this trap."""
    results = evaluate_thresholds([], ["p(95)<250"])

    assert results[0].passed is False
