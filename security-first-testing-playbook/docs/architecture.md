# Architecture

## The shape of the thing

```
src/stplaybook/
├── errors.py        every failure mode, named, with structured attributes
├── clock.py         the only source of time
├── money.py         Naira over integer kobo; split_bill
├── nuban.py         CBN check digits
├── identifiers.py   UUID v4 pattern
├── config.py        environment, validated at boot
│
├── ledger.py        ─┐
├── invoicing.py      ├─ the domain under test
├── parsing.py       ─┘
│
├── authz/           who may do what — the knowledge no scanner has
├── quality/         risk banding, coverage gates, test auditing
├── security/        triage, SBOM, VEX, provenance
└── slo.py           percentiles and threshold evaluation
```

## Three decisions that shape everything else

### 1. No runtime dependencies

`pip install security-first-testing-playbook` pulls nothing. The package is
Python 3.12 standard library throughout.

This is an argument, not an accident. A repository whose central claim is that
every dependency is a component you must trust cannot credibly arrive with a
dependency tree. It also means the default test suite cannot be broken by a
transitive change in somebody else's release, which is the property that makes a
teaching repository still work three years later.

The cost is real: `security/sbom.py` hand-parses CycloneDX rather than using a
library. For the question being asked — *which components are in this build?* —
that is roughly eighty lines, and those eighty lines are readable.

### 2. Offline by construction

The full suite runs with no Docker, no network, no credentials and no services.
Everything that would need them is behind an environment variable and a pytest
marker, and skips cleanly when absent.

The reason is pedagogical as much as practical. A student who cannot run the
suite on the machine in front of them does not run it, and a test suite that is
not run is documentation with extra steps.

### 3. One domain, many lenses

The invoice service is deliberately the single subject of the contract tests, the
abuse-case tests and the authorisation matrix. Three suites verifying one system
find contradictions between their assumptions; three suites verifying three
imagined systems cannot.

## Dependency direction

```
        errors ← everything
         clock ← ledger, invoicing
         money ← ledger, invoicing, parsing
         nuban ← ledger, factories
                     ↓
   ledger · invoicing · parsing        (domain)
                     ↓
      authz · quality · security · slo (analysis)
```

Nothing in `authz`, `quality`, `security` or `slo` is imported by the domain.
The analysis layer observes; it is never observed. This is why the quality
modules can be lifted into another codebase without dragging the invoice
service along.

## Error design

One hierarchy, rooted at `PlaybookError`, with structured attributes:

```python
class DailyLimitExceeded(LedgerError):
    def __init__(self, limit, already_spent, attempted) -> None:
        ...
        self.limit = limit
        self.already_spent = already_spent
        self.attempted = attempted
```

A test asserts `err.value.limit == Naira(200_000)` rather than matching a message
string. Messages are for humans and change freely; attributes are the contract.

Two error pairs are deliberately *indistinguishable at the boundary* while
distinct internally. `InvoiceNotFound` and `TenantMismatch` both render as 404,
because a 403 confirms the resource exists. The repository still raises them
separately, so internal logic and logs retain the distinction the API withholds.

## Determinism

Every time-dependent component takes a `Clock`; every random-dependent one takes
a seeded `random.Random`. Neither is optional and neither has an ambient
fallback in tests.

The consequence is that a test failing at month end, in a different timezone, or
once in fifty runs is treated as a design defect rather than as bad luck — which
is slide 24's argument, enforced by the type signatures.

## Where the boundaries are drawn honestly

* **Provenance verification is offline.** Digest, builder allow-list, source URI.
  No signature cryptography, no Rekor lookup. `docs/security.md` says what a
  production verifier must add.
* **Contract verification is in-process.** It replays a real pact document
  against the real provider, but does not speak to a broker.
* **The Postgres test asserts isolation, not row-level security.** Demonstrating
  database-enforced RLS needs schema and policy definitions beyond this
  repository's scope; the test verifies that the same assertions hold against a
  real engine.

Each of these is a place where the repository could claim more than it does. The
boundary is documented instead.
