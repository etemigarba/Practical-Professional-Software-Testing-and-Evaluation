# Instructor Guide

## You do not need permission

Adopt this, edit it, translate it, teach from it, charge for the course you build
on it. The licence says so explicitly so that nobody writes an email and waits
for a reply. Fork it — your changes stay yours and you skip a review cycle.

## What the repository is for

The deck makes arguments. This repository is where students find out whether the
arguments survive contact with a keyboard. Every claim that can be executed is
executed, and twelve places where the slides were wrong are corrected and
documented in `docs/slide-to-code-map.md`.

That last part is the most useful teaching material here. Students rarely see a
worked example of *reading code critically rather than transcribing it*.

## Prerequisites for students

* Python 3.12 or later
* Ability to run `pip install -e ".[dev]"` and `pytest`
* No Docker, no cloud account, no network beyond the initial install

The second install is the one that matters. Nothing else is needed, on any
platform, for the full suite.

## A twelve-week shape

| Week | Deck | Repository | Exercise |
|---|---|---|---|
| 1 | Foundations, ISO/IEC 25010 | `quality/risk.py` | Band five components of a system they know; defend the reasoning |
| 2 | Test strategy, exit criteria | `quality/coverage.py` | Write a one-page strategy for their own project |
| 3 | Pyramid, FIRST, AAA | `tests/unit/test_ledger.py` | Add a currency-conversion rule with tests |
| 4 | Assertion craft | `tests/unit/test_assertion_craft.py` | Find the weak assertions in a supplied suite |
| 5 | Test doubles | `tests/unit/test_doubles.py` | Replace a mock with a fake; explain what changed |
| 6 | Property-based testing | `tests/property/` | Write a property for a rounding rule |
| 7 | Mutation testing | `quality/coverage.py` | Run `make mutation`; kill three survivors |
| 8 | Integration, contract | `tests/contract/` | Add an interaction to the pact; break the provider |
| 9 | Threat modelling | `tests/security/test_abuse_cases.py` | STRIDE a feature; write one test per threat |
| 10 | Authorisation | `authz/` | Add a `finance_approver` role; watch the matrix grow |
| 11 | Supply chain | `security/` | Verify a tampered artefact; write a VEX statement |
| 12 | Governance, metrics | `docs/governance.md` | Produce an evidence pack for one release |

Weeks 3–7 are the technical core. If the module is shorter, cut weeks 1–2 and
11–12 before cutting those.

## Exercises that reliably work

### The mutation hunt (week 7)

```bash
pip install -e ".[mutation]"
make mutation
```

Students find mutants that survived, then write a test that kills each. This does
more to teach the difference between *executed* and *verified* than any amount of
explanation.

### The matrix growth (week 10)

Add one principal to `PrincipalName` in `authz/policy.py`. Run the tests. Three
new cases fail immediately, because the policy does not yet say what the new role
may do.

The lesson lands without being stated: enumeration turns an oversight into a
failing test.

### Break the parser (week 6 or 9)

```bash
pip install -e ".[fuzz]"
STP_ENABLE_FUZZ=1 python tests/fuzz/fuzz_statement_parser.py -atheris_runs=200000
```

Then: remove a bound from `parsing.py` and run it again. Students see the fuzzer
find the input they would never have written.

### The critical-reading exercise

Give students slide 20 and slide 33 without the corrections, and ask what is
wrong. Slide 20's unbound `invoice_id` is findable by anyone who reads carefully.
Slide 33's `in (401, 404)` is findable only by someone thinking about what the
assertion *permits*. The gap between those two difficulties is the lesson.

## Assessment

The repository suits the 20/20/20/40 weighting used across this course library:

| Component | Weight | Suggested form |
|---|---|---|
| Continuous exercises | 20% | Weekly exercises above |
| Mid-semester | 20% | Written: critique a supplied test suite; name every weakness |
| Practical | 20% | Add a feature to this repository with tests that pass `make verify` |
| Final project | 40% | Apply the full pipeline to a project of their own: strategy, risk banding, tests at four levels, threat model, CI gates, evidence pack |

For the practical, `make verify` is the marking scheme. It is objective, it runs
on the student's machine before submission, and it removes the argument about
whether the work was finished.

## Adapting for a shorter course

* **One-day workshop** — slides 14–25 with the unit, property and mutation
  exercises. Everything runs offline, so a room with poor wifi is not a problem.
* **Security-only module** — Part 3 of the deck with `authz/` and `security/`.
  Weeks 9–11 above stand alone.
* **Postgraduate seminar** — start from `docs/slide-to-code-map.md` and treat the
  twelve corrections as the syllabus.

## Localisation notes

Currency, account numbers and regulatory references are Nigerian: ₦ amounts, CBN
NUBAN check digits, the NDPA 2023 and GAID 2025. Replacing them is a
half-hour job and a reasonable first exercise for a student — `money.py`,
`nuban.py` and `tests/factories.py` are the three files involved.

The compliance map in `docs/governance.md` covers the EU CRA, NDPA, NIST SSDF and
PCI DSS. Substitute your own jurisdiction's instruments; the structure holds.
