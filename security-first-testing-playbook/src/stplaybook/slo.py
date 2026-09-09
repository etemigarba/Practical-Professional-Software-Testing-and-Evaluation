"""Percentiles and k6-style threshold evaluation.

Slide 40's point is that the mean lies.  The illustrated profile has a p50 of
42 ms and a p99.9 of 1,850 ms; an average would hide the tail entirely.  This
module computes percentiles by **nearest rank** — stated explicitly, because
percentile definitions differ and an unstated one makes a reported number
unreproducible.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Final

from .errors import ThresholdSyntaxError

__all__ = ["Threshold", "ThresholdResult", "evaluate_thresholds", "parse_threshold", "percentile"]

_THRESHOLD = re.compile(
    r"^\s*(?:p\((?P<pct>\d+(?:\.\d+)?)\)|(?P<agg>avg|min|max|med|count))"
    r"\s*(?P<op>[<>]=?)\s*(?P<value>\d+(?:\.\d+)?)\s*$"
)
_AGGREGATES: Final = {"avg", "min", "max", "med", "count"}


def percentile(samples: list[float], pct: float) -> float:
    """Return the nearest-rank percentile of ``samples``.

    The nearest-rank value is always an observed sample, never an interpolation
    between two, which is the property you want when reporting a latency an
    actual request experienced.
    """
    if not samples:
        raise ValueError("percentile requires at least one sample")
    if not 0 < pct <= 100:
        raise ValueError("percentile must be in (0, 100]")
    ordered = sorted(samples)
    rank = math.ceil(pct / 100 * len(ordered))
    return ordered[max(0, rank - 1)]


@dataclass(frozen=True)
class Threshold:
    """One parsed k6-style threshold, e.g. ``p(95)<250``."""

    metric: str
    operator: str
    value: float
    expression: str

    def evaluate(self, samples: list[float]) -> float:
        """Compute this threshold's observed statistic over ``samples``."""
        if self.metric.startswith("p("):
            return percentile(samples, float(self.metric[2:-1]))
        if self.metric == "avg":
            return sum(samples) / len(samples)
        if self.metric == "min":
            return min(samples)
        if self.metric == "max":
            return max(samples)
        if self.metric == "med":
            return percentile(samples, 50)
        return float(len(samples))


@dataclass(frozen=True)
class ThresholdResult:
    """The outcome of one threshold against one sample set."""

    threshold: Threshold
    observed: float
    passed: bool

    def describe(self) -> str:
        verdict = "PASS" if self.passed else "FAIL"
        return f"{verdict} {self.threshold.expression} (observed {self.observed:.2f})"


def parse_threshold(expression: str) -> Threshold:
    """Parse ``p(95)<250``, ``avg<100``, and similar, or raise."""
    match = _THRESHOLD.match(expression)
    if match is None:
        raise ThresholdSyntaxError(expression)
    pct, agg = match.group("pct"), match.group("agg")
    metric = f"p({pct})" if pct is not None else str(agg)
    return Threshold(
        metric=metric,
        operator=match.group("op"),
        value=float(match.group("value")),
        expression=expression.strip(),
    )


def evaluate_thresholds(samples: list[float], expressions: list[str]) -> list[ThresholdResult]:
    """Evaluate every threshold, returning one result each.

    A threshold with no samples to draw on is reported as **failing**, not as
    vacuously passing.  Slide 40's ``checks: ["rate>0.99"]`` with no ``check()``
    calls is exactly the vacuous gate this refuses to reproduce.
    """
    results: list[ThresholdResult] = []
    for expression in expressions:
        threshold = parse_threshold(expression)
        if not samples:
            results.append(ThresholdResult(threshold, observed=float("nan"), passed=False))
            continue
        observed = threshold.evaluate(samples)
        passed = {
            "<": observed < threshold.value,
            "<=": observed <= threshold.value,
            ">": observed > threshold.value,
            ">=": observed >= threshold.value,
        }[threshold.operator]
        results.append(ThresholdResult(threshold, observed, passed))
    return results
