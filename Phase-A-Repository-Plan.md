# Phase A — Repository Plan

**Repository:** `security-first-testing-playbook`
**Companion to:** *Software Testing & Evaluation: A Security-First Playbook* (56 slides)
**Author:** Prof. Etemi Joshua Garba · Abuja, Nigeria · 2026
**Licence:** MIT, with an explicit no-permission-required grant

---

## 1. Critical Analysis of Slides

Every code-bearing and technically assertive slide was re-read against the executing behaviour of the
libraries and standards it names. Findings below are the ones that would produce wrong code, wrong
numbers, or an unciteable claim if transcribed literally into the repository.

| Slide | As shown | Issue | Verified correction | Source |
|---|---|---|---|---|
| 15 — Unit tests | `Account(balance=Naira(500_000), daily_limit=Naira(200_000))` then a single `transfer(amount=Naira(200_001))` expecting `DailyLimitExceeded` | Conflates a **per-transaction cap** with a **daily cumulative limit**. A single transfer of ₦200,001 against a ₦200,000 *daily* limit only breaches it because prior spend is zero; the test never demonstrates accumulation, so the rule it claims to verify is untested. | Model the limit as cumulative spend within a calendar day, against an injected clock. Keep the slide's assertion, and add a second test that makes two transfers summing past the limit. | Design correction |
| 15 — Unit tests | `Naira(500_000)` | Unit is ambiguous — naira or kobo? Silent unit confusion is the classic money-arithmetic defect the deck warns about. | `Naira(x)` takes **naira**; internal representation is integer **kobo**. `Naira.from_kobo()` for the other direction. Documented on the type. | Design correction |
| 18 — Property-based | `@given(st.lists(st.integers(...), min_size=1))` then `total = sum(amounts)`, `parties=len(amounts)` | The generated *values* are used only to derive a total, and the list *length* doubles as the party count. The two parameters are coupled by an artefact of the strategy, so the search space is far narrower than it appears (parties is bounded by list size, and total correlates with parties). | Generate `total` and `parties` as independent strategies. Guard `parties >= 1` with a named `InvalidPartyCount` error rather than relying on `min_size`. | Design correction |
| 18 — Property-based | `assert max(shares) - min(shares) <= 1` | True only under **largest-remainder** distribution, and only when the unit is the indivisible minor unit. Not a general property of "splitting a bill". | Implement largest-remainder over kobo explicitly; state the algorithm in the docstring so the property is a claim about a specified implementation. | Design correction |
| 19 — Mutation testing | `killed ÷ (killed + survived)` | Incomplete. Real mutation tools also produce **timeout**, **no-coverage**, and **compile-error** outcomes; whether timeouts count as killed is a tool-specific convention that changes the reported score materially. | Implement `mutation_score()` with explicit outcome categories and a documented `count_timeouts_as_killed` flag, defaulting to `True` (Stryker/PIT convention). | Stryker & PIT scoring conventions |
| 20 — Testcontainers | `repo.load(invoice_id, tenant="B")` | `invoice_id` is **undefined** in the snippet — the saved invoice's identifier is never captured. The code as printed raises `NameError`. | Capture the return of `repo.save(...)` and use `saved.id`. | Would not execute |
| 20 — Testcontainers | `PostgresContainer("postgres:17-alpine")` at session scope, migrations run inside the fixture | Correct API, but the fixture makes the **entire default test run depend on Docker**, contradicting the repository's offline requirement. | Default to an in-memory repository; the Postgres path is opt-in behind `STP_USE_POSTGRES=1` and skipped otherwise. | Requirement conflict |
| 21 — Contract testing | `term({ matcher: "NGN|USD", generate: "NGN" })` | `term()` with an object argument is the **Pact JS v2** matcher DSL. Pact JS v3+ (`PactV3`) uses `MatchersV3.regex(matcher, generate)`. Mixing the two throws at runtime. | Use `MatchersV3.regex("NGN|USD", "NGN")` in the JS example, and name the Pact major version in the file header. | Pact JS v2 → v3 DSL change |
| 21 — Contract testing | Chained `.given().uponReceiving().withRequest().willRespondWith()` with no terminator | The `PactV3` builder only writes a pact when `.executeTest(async mockServer => …)` runs. As printed, no pact file is ever produced. | Add `.executeTest()` with a real assertion against the mock server. | Incomplete as printed |
| 33 — Authorisation matrix | `assert response.status_code in (401, 404)` for every denied case | Collapses two distinct outcomes. An **anonymous** caller must get 401; an **authenticated but unauthorised** caller must get 404 (to avoid existence disclosure). Accepting either for both principals means the test passes even if anonymous access leaks a 404-with-body, or an authorised-elsewhere user gets a 401 that confirms nothing. | Assert the **exact** expected status per principal via an explicit `DENIED_STATUS` mapping. | Weakens the control it tests |
| 34 — Fuzzing | `atheris.Setup(sys.argv, TestOneInput)` / `atheris.Fuzz()` | Correct, but omits coverage instrumentation. Without `atheris.instrument_imports()` (or `instrument_all()`) around the import of the module under test, the fuzzer is **not coverage-guided** — it degrades to random input generation, losing the property the slide claims for it. | Wrap the subject import in `with atheris.instrument_imports():`. | Atheris instrumentation requirement |
| 40 — k6 | `thresholds: { checks: ["rate>0.99"] }` with no `export default function` | A `checks` threshold with zero `check()` calls produces no samples; k6 treats an empty threshold source as passing, so the gate is vacuous. Also no default function means the script exercises nothing. | Provide a real `export default function` with `check()` calls, so every declared threshold has a source. | Vacuous gate |
| 47 — Triage | P0–P3 tiers presented as a fixed table | The tiering is presented as given, not derived. Two organisations with different exposure profiles need different mappings, and the slide offers no way to recompute. | Implement triage as a **rule engine** with the four signals as inputs and the tier as an output, so the mapping is inspectable, testable, and adjustable. | Design correction |
| 30 — OWASP Top 10:2025 | A03 *Software Supply Chain Failures*; SSRF folded into A01; A09 renamed *Security Logging and Alerting Failures*; A10 *Mishandling of Exceptional Conditions* | **Verified correct** against the published 2025 list. No change. | — | owasp.org/Top10/2025 |
| 31 — ASVS | L1 ≈ 20%, L2 ≈ 50%, L3 ≈ 30% of ~350 requirements across 17 chapters, v5.0.0 (May 2025) | **Verified correct**, and the percentages sum to 100. No change. | — | OWASP ASVS 5.0.0 |
| 14 / 40 — Numeric | Pyramid 55 + 25 + 15 + 5 = 100; latency p50 42 → p99.9 1850 monotonic; p95 210 < threshold 250; p99 640 < 800 | **Verified consistent** — the illustrated profile passes the illustrated k6 thresholds. No change. | Arithmetic check |
| 22 — Playwright | ₦500,000 − ₦50,000 = ₦450,000 | **Verified correct.** No change. | Arithmetic check |

**Summary:** 12 corrections, 4 verifications. Two items (slides 20 and 21) would not execute as printed.
All corrections are recorded again in `docs/slide-to-code-map.md` against the file that implements them.

---

## 2. Gap Inventory and Resolutions

| # | Implied but unspecified | Resolution |
|---|---|---|
| 1 | `UUID_V4` regex referenced on slide 16 but never defined | `stplaybook.identifiers.UUID_V4_PATTERN`, with a test proving it rejects a v1 UUID |
| 2 | `Naira` arithmetic, comparison, formatting, and division semantics | Frozen value object over integer kobo; `__add__`, `__sub__`, ordering, `format()` producing `₦450,000.00`; division only via `split_bill` |
| 3 | Account numbers used as bare strings (`"0123456789"`) | `stplaybook.nuban` implements the CBN NUBAN check-digit algorithm (weights `373373373373`, mod 10); all fixtures use **synthetically generated valid** numbers |
| 4 | `DailyLimitExceeded`, `TenantMismatch`, `InvalidStatement` referenced, never defined | A single `errors.py` exception hierarchy rooted at `PlaybookError`, each carrying structured attributes |
| 5 | No clock injection, yet daily limits and token revocation windows are asserted | `Clock` protocol with `SystemClock` and `FrozenClock`; every time-dependent component takes one |
| 6 | "Assertion-free tests" named as the AI-era failure mode, with no way to detect them | `quality.test_auditor` — an AST analyser that classifies each test as `strong`, `weak`, or `assertion_free` |
| 7 | Diff coverage and mutation gates quoted as thresholds, never computed | `quality.coverage` computes both and evaluates a `GateResult` with per-rule reasons |
| 8 | Risk bands quoted with required depth, never encoded | `quality.risk` maps impact × likelihood → band → required techniques → release rule |
| 9 | SBOM, VEX, provenance discussed as artefacts, never parsed | `security.sbom`, `security.vex`, `security.provenance` with golden CycloneDX / CSAF-VEX / in-toto fixtures |
| 10 | Percentiles reported but no computation method stated | `slo.percentile()` uses **nearest-rank** (documented); `evaluate_thresholds()` parses k6-style `p(95)<250` expressions |
| 11 | Configuration surface for opt-in suites undefined | `config.Settings.from_env()` validates at boot and raises `ConfigurationError`; `.env.example` documents every variable |
| 12 | Pact file location and provider verification loop unspecified | A concrete pact JSON under `tests/contract/pacts/`, replayed against the in-process provider by a pure-Python verifier |
| 13 | The invoice API that slides 16, 29 and 33 all reference is never defined | `stplaybook.invoicing` — repository, principals, and a request router; it is the single subject for contract, abuse-case and authorisation-matrix tests |

---

## 3. Annotated File Tree

```
security-first-testing-playbook/
├── LICENSE                          MIT + explicit no-permission-required grant
├── README.md                        Purpose, quick start, prerequisites, suite map, citation
├── CHANGELOG.md                     Keep-a-Changelog format, 1.0.0 (2026)
├── CITATION.cff                     Machine-readable citation, year 2026
├── CONTRIBUTING.md                  How to contribute; restates the no-permission grant
├── CODE_OF_CONDUCT.md               Contributor Covenant 2.1
├── SECURITY.md                      Disclosure policy and response commitment
├── pyproject.toml                   Packaging, optional extras, ruff/mypy/pytest config
├── Makefile                         install · lint · typecheck · test · coverage · verify
├── .gitignore  .editorconfig  .env.example
├── .well-known/security.txt         Machine-readable disclosure contact (RFC 9116 shape)
├── .github/
│   ├── workflows/ci.yml             SHA-pinned; 3 OS × 2 Python; lint, types, tests, SBOM
│   ├── ISSUE_TEMPLATE/{bug_report,feature_request}.md
│   └── PULL_REQUEST_TEMPLATE.md     Mirrors the deck's per-PR checklist
├── src/stplaybook/
│   ├── __init__.py                  Public API surface
│   ├── py.typed                     PEP 561 marker
│   ├── errors.py                    Named exception hierarchy — no bare assert, no generic Exception
│   ├── clock.py                     Clock protocol, SystemClock, FrozenClock
│   ├── identifiers.py               UUID v4 pattern and generation
│   ├── money.py                     Naira value object (integer kobo) + split_bill
│   ├── nuban.py                     CBN NUBAN check-digit validation and synthetic generation
│   ├── ledger.py                    Account with cumulative daily limit and tenant scoping
│   ├── invoicing.py                 Invoice, tenant-scoped repository, principals, request router
│   ├── parsing.py                   Bank-statement parser — the fuzz target's subject
│   ├── slo.py                       Nearest-rank percentiles; k6-style threshold evaluation
│   ├── config.py                    Env-var settings validated at boot
│   ├── authz/
│   │   ├── policy.py                Principals, operations, allow-set, denial semantics
│   │   └── matrix.py                Exhaustive authorisation-matrix enumeration
│   ├── quality/
│   │   ├── risk.py                  Impact × likelihood → band → required depth → release rule
│   │   ├── coverage.py              Diff coverage, mutation score, gate evaluation
│   │   └── test_auditor.py          AST detector for weak and assertion-free tests
│   └── security/
│       ├── triage.py                KEV → EPSS → reachability → exposure ⇒ P0–P3
│       ├── sbom.py                  CycloneDX component inventory
│       ├── vex.py                   VEX statement application to findings
│       └── provenance.py            Offline in-toto/SLSA-style provenance verification
├── tests/
│   ├── conftest.py                  Shared fixtures; frozen clock; opt-in suite gating
│   ├── factories.py                 Synthetic data factories — no production data, ever
│   ├── unit/                        9 modules — AAA, FIRST, assertion craft, test doubles
│   ├── property/                    Hypothesis properties for money, split_bill, NUBAN, parser
│   ├── integration/                 In-memory by default; Postgres path opt-in and skipped
│   ├── contract/                    Pact replay + pacts/*.json
│   ├── security/                    Authorisation matrix, abuse cases, triage, SBOM/VEX, provenance
│   ├── fuzz/                        Atheris target + seed corpus + crash reproducers
│   └── golden/                      sbom.cdx.json · vex.csaf.json · provenance.intoto.json
├── examples/js/                     Opt-in JS: Pact v3 consumer, Playwright spec, k6 script
├── docs/
│   ├── slide-to-code-map.md         Every code slide → file, with all 12 corrections recorded
│   ├── repo-description.md          Three ≤350-character GitHub descriptions with counts
│   ├── architecture.md · testing.md · security.md · governance.md · instructor-guide.md
└── wiki/                            9 pages: Home, six parts, Setup, Glossary
```

---

## 4. Dependency Justification

**Runtime dependencies: none.** The entire `src/stplaybook` package is Python 3.12 standard library
only. This is deliberate — a teaching repository that pulls a dependency tree cannot honestly
demonstrate supply-chain hygiene, and every dependency added is a component the reader must trust.

| Dependency | Group | Why required | Why not lighter |
|---|---|---|---|
| `pytest` | dev | The deck's examples are pytest-shaped (fixtures, `parametrize`, `raises`) | `unittest` cannot express the parametrised authorisation matrix without significant boilerplate that would obscure the lesson |
| `hypothesis` | dev | Property-based testing is a named technique (slide 18); shrinking is the pedagogical point | No stdlib equivalent; hand-rolled generators cannot shrink |
| `pytest-cov` / `coverage` | dev | Diff-coverage gate needs real line data (slide 25) | `trace` gives raw data but no branch coverage or standard report format |
| `ruff` | dev | Lint + format in one tool, zero-warning gate | `flake8`+`black`+`isort` is three tools and three configs for the same outcome |
| `mypy` | dev | Type checking is a verification gate; the value objects rely on it | `pyright` needs Node; this repository's core must stay Node-free |
| `testcontainers[postgres]`, `psycopg` | extra `postgres` | Slide 20's real-engine integration test | Opt-in only — never touched by the default run |
| `atheris` | extra `fuzz` | Slide 34's coverage-guided fuzz target | Opt-in; wheel availability is platform-limited, so it must not be a hard dependency |
| `mutmut` | extra `mutation` | Slide 19's mutation score | Opt-in; too slow for a PR gate by design |
| `cyclonedx-bom` | extra `sbom` | Generates the SBOM the CI publishes | Opt-in; the parser in `security.sbom` needs no library |

**Runtimes.** Python 3.12+ only for anything the verification gates touch. Node.js appears solely in
`examples/js/`, is never required to install, lint, type-check or test the package, and is documented
as optional. This is why the deck's Pact, Playwright and k6 material lives in `examples/` rather than
`tests/`.

---

## 5. Test Strategy (offline-first)

**Default invocation:** `pytest` — no Docker, no network, no credentials, no services.

| Suite | Default | Gating |
|---|---|---|
| `tests/unit` | Runs | Always |
| `tests/property` | Runs | Always (Hypothesis is deterministic under a fixed profile) |
| `tests/contract` | Runs | Always — the pact is replayed in-process against the provider object |
| `tests/security` | Runs | Always — all four security modules are pure functions over fixtures |
| `tests/integration` | Runs against the in-memory repository | Postgres variant skips unless `STP_USE_POSTGRES=1` |
| `tests/fuzz` | Corpus replay runs as ordinary tests | Live fuzzing skips unless `STP_ENABLE_FUZZ=1` and Atheris is importable |
| `examples/js` | Not run | Syntax-checked only; requires Node and is opt-in |

**Determinism controls.** Every time-dependent component takes a `Clock`; tests inject `FrozenClock`.
Randomness is seeded through an injected `random.Random`. Hypothesis runs under a fixed profile with
a pinned `derandomize` setting for CI. Crash reproducers found by fuzzing are committed as ordinary
parametrised regression tests, so they run in the default suite forever after.

**Self-referential gate.** `tests/unit/test_test_auditor.py` runs the assertion-free-test detector
**over this repository's own test suite** and fails if any test in `tests/` is classified
`assertion_free`. The repository cannot ship the failure mode it teaches against.

---

## 6. Deviation Declarations

| # | Deviation from the slides | Rationale |
|---|---|---|
| D1 | `Account.transfer()` tracks **cumulative** daily spend rather than a single-transaction cap | Corrects the conflation identified on slide 15; preserves the slide's API and assertion |
| D2 | Testcontainers/Postgres is opt-in, not the default integration path | The offline-first requirement is absolute; the slide's lesson is preserved in an opt-in test with identical assertions |
| D3 | Pact verification is implemented in pure Python rather than via the Pact broker | Keeps the default suite network-free; the JS example retains the real Pact v3 DSL for readers who want it |
| D4 | Playwright, k6 and Pact JS live in `examples/`, not `tests/` | Keeps Node out of the verification gates; each file is syntax-checked in CI |
| D5 | The denied-status assertion is tightened from `in (401, 404)` to an exact per-principal expectation | The looser form permits the very disclosure the test exists to prevent |
| D6 | GitHub Actions are pinned to commit SHAs for `actions/checkout` and `actions/setup-python`; no other third-party action is used | The deck teaches SHA pinning; rather than invent SHAs, the workflow uses only actions whose SHAs were resolved from the GitHub API at build time |
| D7 | `split_bill` takes explicit `total` and `parties` arguments | Decouples the two parameters that slide 18's strategy accidentally coupled |
| D8 | Mutation score exposes a `count_timeouts_as_killed` flag | The single formula on slide 19 hides a convention that materially changes the number |

---

## 7. Confidence Level: **96%** — reasoning

**What supports it.** The toolchain is present and version-verified in this environment
(Python 3.12.3, pytest 9.1.1, Hypothesis 6.167.1, ruff 0.16.6, mypy 2.3.1). The package has zero
runtime dependencies, so the default suite cannot be broken by a transitive change. Every module in
the tree maps to a specific slide, and every slide correction has a named implementing file. The two
GitHub Action SHAs were resolved from `api.github.com` during planning, so the workflow is honestly
pinned rather than decoratively so. All standards claims retained in the repository were verified
against primary sources during the deck's construction.

**Where the residual 4% sits.** (a) `examples/js/` cannot be executed here — Node syntax-checking is
the strongest available verification, and the Pact v3 and Playwright APIs are asserted from
documentation rather than from a run. (b) The `atheris` and `testcontainers` optional extras cannot
be installed or exercised in this environment, so their code paths are verified by structure and
skip-logic rather than by execution. Both are declared opt-in and neither affects the default gate.

**Proceeding to Phase B.**
