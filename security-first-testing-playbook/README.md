# Security-First Testing Playbook

[![CI](https://github.com/etemigarba/security-first-testing-playbook/actions/workflows/ci.yml/badge.svg)](https://github.com/etemigarba/security-first-testing-playbook/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
[![Licence: MIT](https://img.shields.io/badge/licence-MIT-green)](LICENSE)
[![Runtime dependencies: 0](https://img.shields.io/badge/runtime%20dependencies-0-brightgreen)](pyproject.toml)
[![Type checked: mypy strict](https://img.shields.io/badge/mypy-strict-informational)](pyproject.toml)

Runnable companion to the 56-slide course deck ***Software Testing & Evaluation:
A Security-First Playbook*** by **Prof. Etemi Joshua Garba** (Abuja, Nigeria,
2026).

Every code-bearing slide in that deck is implemented here as tested, working
Python — and the twelve places where the slides were *wrong* are corrected, with
each correction documented and pinned by a test.

```bash
git clone https://github.com/etemigarba/security-first-testing-playbook
cd security-first-testing-playbook
pip install -e ".[dev]"
pytest
```

That is the whole setup. **No Docker, no network, no credentials, no services.**
139 tests in about a second.

---

## Why this repository exists

Testing decks are full of code that has never been run. Slide 20's example raises
`NameError` as printed. Slide 21's Pact chain writes no pact file. Slide 33's
denial assertion passes even when the control it guards is broken.

This repository runs everything, and says so where the slides were wrong.

It also holds itself to its own arguments:

* **Zero runtime dependencies.** A repository arguing that every dependency is a
  component you must trust should not arrive with a dependency tree.
* **A gate against its own failure mode.** `make audit` runs an AST detector for
  assertion-free tests across this repository's own suite. CI fails if it finds
  one.
* **Every boundary stated.** Provenance verification is offline; that limit is
  documented rather than glossed.

---

## Prerequisites

| | Required | Version |
|---|---|---|
| Python | Yes | 3.12 or later |
| pip | Yes | any recent |
| Docker | **No** | only for the opt-in Postgres test |
| Node.js | **No** | only for the optional JS examples |
| Network | **No** | only for the initial `pip install` |

Tested on Linux, macOS and Windows, against Python 3.12 and 3.13.

---

## Installation

```bash
pip install -e ".[dev]"                 # package + test toolchain

# Optional extras, none required:
pip install -e ".[postgres]"            # real-engine integration test
pip install -e ".[fuzz]"                # coverage-guided fuzzing
pip install -e ".[mutation]"            # mutation testing
pip install -e ".[sbom]"                # SBOM generation
```

---

## Running the suites

```bash
make verify        # lint + typecheck + test + audit — exactly what CI runs
make test          # pytest
make coverage      # with branch coverage
make audit         # fail on any assertion-free test
make mutation      # nightly, opt-in
make fuzz          # opt-in
make sbom          # generate a CycloneDX SBOM
```

Opt-in suites, each skipping cleanly when absent:

```bash
STP_USE_POSTGRES=1 pytest tests/integration
STP_ENABLE_FUZZ=1 python tests/fuzz/fuzz_statement_parser.py -atheris_runs=200000
```

Every switch is documented in `.env.example` and validated at boot by
`src/stplaybook/config.py`.

---

## Repository map

| Path | What is in it |
|---|---|
| `src/stplaybook/` | The package. Standard library only. |
| `src/stplaybook/errors.py` | Every failure mode, named, with structured attributes |
| `src/stplaybook/money.py` | `Naira` over integer kobo; largest-remainder `split_bill` |
| `src/stplaybook/nuban.py` | CBN NUBAN check digits |
| `src/stplaybook/ledger.py` | Cumulative daily limits against an injected clock |
| `src/stplaybook/invoicing.py` | Tenant-scoped repository and API — the shared subject |
| `src/stplaybook/parsing.py` | Bounded statement parser, the fuzz target's subject |
| `src/stplaybook/authz/` | Authorisation policy and exhaustive matrix enumeration |
| `src/stplaybook/quality/` | Risk banding, coverage gates, assertion-free test auditor |
| `src/stplaybook/security/` | Triage, SBOM, VEX, provenance |
| `src/stplaybook/slo.py` | Nearest-rank percentiles, k6-style thresholds |
| `tests/` | Unit, property, contract, integration, security, fuzz |
| `docs/` | Slide-to-code map, architecture, testing, security, governance, instructor guide |
| `wiki/` | Nine pages, one per part of the deck plus setup and glossary |
| `examples/js/` | Optional Pact v3, Playwright and k6 examples |

---

## How it maps to the deck

| Part | Deck topic | Here |
|---|---|---|
| 1 | Foundations, ISO/IEC 25010, risk banding | `quality/risk.py` · `wiki/01-Foundations.md` |
| 2 | Pyramid, FIRST, property, mutation, contract | `tests/unit/` · `tests/property/` · `tests/contract/` |
| 3 | STRIDE, OWASP Top 10:2025, ASVS 5.0, supply chain | `authz/` · `security/` · `tests/security/` |
| 4 | SLOs, chaos, accessibility, progressive delivery | `slo.py` · `examples/js/perf/` |
| 5 | NIST SSDF, triage, metrics, compliance | `security/triage.py` · `docs/governance.md` |
| 6 | Anti-patterns, checklist, roadmap | `docs/instructor-guide.md` · `wiki/06-Adoption.md` |

---

## A worked example

Slide 15's test, corrected. The slide asserts a *daily* limit but exercises only
a single transfer, so the accumulation it describes is never tested:

```python
def test_transfer_rejects_amount_above_daily_limit(account: Account) -> None:
    with pytest.raises(DailyLimitExceeded) as err:
        account.transfer(to="0123456789", amount=Naira(200_001))

    assert err.value.limit == Naira(200_000)
    assert account.balance == Naira(500_000)   # nothing was mutated


def test_daily_limit_is_cumulative_not_per_transaction(account: Account) -> None:
    account.transfer(to="0123456789", amount=Naira(150_000))

    with pytest.raises(DailyLimitExceeded) as err:
        account.transfer(to="0123456789", amount=Naira(60_000))

    assert err.value.already_spent == Naira(150_000)
    assert account.balance == Naira(350_000)
```

The second assertion in the first test is the one people leave out. It proves the
rejection did not half-happen.

All twelve corrections are in **[`docs/slide-to-code-map.md`](docs/slide-to-code-map.md)**.

---

## Licence and reuse

MIT, **Copyright (c) 2026 Prof. Etemi Joshua Garba**, with an explicit additional
grant:

> No explicit permission is required to adopt, edit, refactor, translate, teach
> from, redistribute, or commercially use this work, in whole or in part.

Fork it for your course. Translate it. Rewrite the Nigerian framing for your own
jurisdiction — `money.py`, `nuban.py` and `tests/factories.py` are the three
files involved. Build paid training on it. You need not ask, and you need not
wait for a reply.

Full terms in [`LICENSE`](LICENSE).

---

## Citation

```bibtex
@software{garba_2026_security_first_testing,
  author  = {Garba, Etemi Joshua},
  title   = {Security-First Testing Playbook},
  year    = {2026},
  version = {1.0.0},
  license = {MIT},
  url     = {https://github.com/etemigarba/security-first-testing-playbook}
}
```

Machine-readable form in [`CITATION.cff`](CITATION.cff).

---

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Security issues go through
[`SECURITY.md`](SECURITY.md), not the issue tracker.

**Year of development: 2026.**
