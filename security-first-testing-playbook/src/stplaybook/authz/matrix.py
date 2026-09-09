"""Exhaustive enumeration of principals x operations.

Slide 33's argument is that the matrix must be *enumerated*, not sampled: when a
new role or endpoint is added the matrix grows automatically, so a coverage gap
becomes a failing test rather than an oversight nobody noticed.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Final, get_args

from .policy import DEFAULT_POLICY, Operation, Policy, PrincipalName

__all__ = ["ALL_OPERATIONS", "ALL_PRINCIPALS", "Expectation", "MatrixCase", "enumerate_matrix"]

ALL_PRINCIPALS: Final[tuple[PrincipalName, ...]] = get_args(PrincipalName)
ALL_OPERATIONS: Final[tuple[Operation, ...]] = get_args(Operation)


@dataclass(frozen=True)
class Expectation:
    """What must happen, and what must not appear when it does not."""

    status: int
    permitted: bool

    @property
    def must_not_disclose(self) -> bool:
        """A denied response must not echo the resource identifier."""
        return not self.permitted


@dataclass(frozen=True)
class MatrixCase:
    """One cell of the authorisation matrix."""

    principal: PrincipalName
    operation: Operation
    expectation: Expectation

    @property
    def id(self) -> str:
        """A stable pytest parameter id."""
        verdict = "allow" if self.expectation.permitted else "deny"
        return f"{self.principal}-{self.operation}-{verdict}{self.expectation.status}"


def enumerate_matrix(policy: Policy = DEFAULT_POLICY) -> tuple[MatrixCase, ...]:
    """Every principal against every operation. No sampling, no omissions."""
    return tuple(
        MatrixCase(
            principal=principal,
            operation=operation,
            expectation=Expectation(
                status=policy.expected_status(principal, operation),
                permitted=policy.permits(principal, operation),
            ),
        )
        for principal, operation in product(ALL_PRINCIPALS, ALL_OPERATIONS)
    )
