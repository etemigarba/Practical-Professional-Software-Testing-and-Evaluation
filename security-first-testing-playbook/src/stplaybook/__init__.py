"""Security-first testing playbook — runnable companion to the 56-slide deck.

Every module here implements a technique the deck demonstrates.  The package has
**no runtime dependencies**: a repository arguing for supply-chain hygiene should
not oblige its readers to trust a dependency tree in order to read it.

Author: Prof. Etemi Joshua Garba, Abuja, Nigeria.
Year of development: 2026.  MIT licensed; no permission required to adopt, edit,
refactor, translate, teach from, or commercially use this work.
"""

from __future__ import annotations

__version__ = "1.0.0"
__author__ = "Prof. Etemi Joshua Garba"
__year__ = "2026"
__license__ = "MIT"

from .clock import Clock, FrozenClock, SystemClock
from .invoicing import ANONYMOUS, Invoice, InvoiceApi, InvoiceRepository, Principal
from .ledger import Account, Transfer
from .money import Naira, split_bill
from .nuban import generate_nuban, is_valid_nuban
from .parsing import Statement, parse_bank_statement
from .slo import evaluate_thresholds, percentile

__all__ = [
    "ANONYMOUS",
    "Account",
    "Clock",
    "FrozenClock",
    "Invoice",
    "InvoiceApi",
    "InvoiceRepository",
    "Naira",
    "Principal",
    "Statement",
    "SystemClock",
    "Transfer",
    "__author__",
    "__license__",
    "__version__",
    "__year__",
    "evaluate_thresholds",
    "generate_nuban",
    "is_valid_nuban",
    "parse_bank_statement",
    "percentile",
    "split_bill",
]
