"""Named exception hierarchy for the playbook.

The deck argues that bare ``assert`` and generic ``Exception`` destroy a test's
ability to say *why* something failed.  Every failure mode in this package
therefore has its own class carrying structured attributes, so a test can assert
on the reason rather than on a message string.
"""

from __future__ import annotations

__all__ = [
    "ConfigurationError",
    "CurrencyMismatch",
    "DailyLimitExceeded",
    "FractionalNaira",
    "InsufficientFunds",
    "InvalidAccountNumber",
    "InvalidPartyCount",
    "InvalidStatement",
    "InvoiceNotFound",
    "InvoicingError",
    "LedgerError",
    "MoneyError",
    "NegativeAmount",
    "ParseError",
    "PlaybookError",
    "ProvenanceRejected",
    "SbomError",
    "SupplyChainError",
    "TenantMismatch",
    "ThresholdSyntaxError",
]


class PlaybookError(Exception):
    """Root of every error raised by this package."""


class ConfigurationError(PlaybookError):
    """Raised at boot when required configuration is absent or malformed."""

    def __init__(self, variable: str, reason: str) -> None:
        super().__init__(f"configuration variable {variable!r} is invalid: {reason}")
        self.variable = variable
        self.reason = reason


class MoneyError(PlaybookError):
    """Base class for monetary faults."""


class NegativeAmount(MoneyError):
    """Raised when an amount would become negative."""

    def __init__(self, kobo: int) -> None:
        super().__init__(f"amount may not be negative (got {kobo} kobo)")
        self.kobo = kobo


class CurrencyMismatch(MoneyError):
    """Raised when two amounts in different currencies are combined."""

    def __init__(self, left: str, right: str) -> None:
        super().__init__(f"cannot combine {left} with {right}")
        self.left = left
        self.right = right


class FractionalNaira(MoneyError):
    """Raised when an amount carrying kobo is asked for as whole naira."""

    def __init__(self, kobo: int) -> None:
        super().__init__(f"{kobo} kobo is not a whole number of naira")
        self.kobo = kobo


class InvalidPartyCount(MoneyError):
    """Raised when a bill is split between fewer than one party."""

    def __init__(self, parties: int) -> None:
        super().__init__(f"a bill must be split between at least one party (got {parties})")
        self.parties = parties


class LedgerError(PlaybookError):
    """Base class for ledger faults."""


class InsufficientFunds(LedgerError):
    """Raised when a transfer exceeds the available balance."""

    def __init__(self, balance: object, attempted: object) -> None:
        super().__init__(f"transfer of {attempted} exceeds balance {balance}")
        self.balance = balance
        self.attempted = attempted


class DailyLimitExceeded(LedgerError):
    """Raised when a transfer would breach the account's cumulative daily limit."""

    def __init__(self, limit: object, already_spent: object, attempted: object) -> None:
        super().__init__(
            f"transfer of {attempted} would breach daily limit {limit} "
            f"(already spent {already_spent} today)"
        )
        self.limit = limit
        self.already_spent = already_spent
        self.attempted = attempted


class InvalidAccountNumber(LedgerError):
    """Raised when an account number fails NUBAN validation."""

    def __init__(self, account_number: str, reason: str) -> None:
        super().__init__(f"account number {account_number!r} is invalid: {reason}")
        self.account_number = account_number
        self.reason = reason


class InvoicingError(PlaybookError):
    """Base class for invoicing faults."""


class InvoiceNotFound(InvoicingError):
    """Raised when no invoice exists for the given identifier."""

    def __init__(self, invoice_id: str) -> None:
        super().__init__(f"no invoice with id {invoice_id!r}")
        self.invoice_id = invoice_id


class TenantMismatch(InvoicingError):
    """Raised when a caller reaches for a resource belonging to another tenant.

    Deliberately indistinguishable from :class:`InvoiceNotFound` at the API
    boundary: confirming that a resource exists is itself a disclosure.
    """

    def __init__(self, invoice_id: str, requested_tenant: str) -> None:
        super().__init__(f"invoice {invoice_id!r} is not visible to tenant {requested_tenant!r}")
        self.invoice_id = invoice_id
        self.requested_tenant = requested_tenant


class ParseError(PlaybookError):
    """Base class for parser faults."""


class InvalidStatement(ParseError):
    """Raised when a byte string is not a well-formed bank statement.

    The fuzzing contract: ``parse_bank_statement`` either returns a consistent
    :class:`~stplaybook.parsing.Statement` or raises this. Nothing else.
    """

    def __init__(self, reason: str, offset: int | None = None) -> None:
        location = "" if offset is None else f" at byte {offset}"
        super().__init__(f"malformed statement{location}: {reason}")
        self.reason = reason
        self.offset = offset


class SupplyChainError(PlaybookError):
    """Base class for supply-chain verification faults."""


class ProvenanceRejected(SupplyChainError):
    """Raised when a build provenance attestation fails verification."""

    def __init__(self, reason: str) -> None:
        super().__init__(f"provenance rejected: {reason}")
        self.reason = reason


class SbomError(SupplyChainError):
    """Raised when an SBOM document cannot be read."""

    def __init__(self, reason: str) -> None:
        super().__init__(f"unusable SBOM: {reason}")
        self.reason = reason


class ThresholdSyntaxError(PlaybookError):
    """Raised when a k6-style threshold expression cannot be parsed."""

    def __init__(self, expression: str) -> None:
        super().__init__(f"cannot parse threshold expression {expression!r}")
        self.expression = expression
