# Slide-to-Code Map

Every code-bearing slide in *Software Testing & Evaluation: A Security-First
Playbook*, mapped to the file that implements it — and every deviation from what
the slide shows, with the reason.

The rule: **no slide code was transcribed uncritically.** Twelve corrections were
made during Phase A analysis. Two of them concern code that would not have
executed as printed.

---

## Part 1 — Foundations

| Slide | Topic | Implemented in |
|---|---|---|
| 9 | Quality attribute → technique map | `src/stplaybook/quality/risk.py` (`Technique`) |
| 10 | Risk-based testing, bands and depth | `src/stplaybook/quality/risk.py` · `tests/unit/test_risk.py` |
| 12 | Entry/exit criteria as machine-checkable gates | `src/stplaybook/quality/coverage.py` (`evaluate_gates`) |

---

## Part 2 — Test architecture

| Slide | Topic | Implemented in |
|---|---|---|
| 15 | FIRST, Arrange–Act–Assert | `tests/unit/test_ledger.py` · `src/stplaybook/ledger.py` |
| 16 | Assertions that actually assert | `tests/unit/test_assertion_craft.py` · `src/stplaybook/identifiers.py` |
| 17 | Five test doubles | `tests/unit/test_doubles.py` |
| 18 | Property-based testing | `tests/property/test_money_properties.py` · `src/stplaybook/money.py` |
| 19 | Mutation testing | `src/stplaybook/quality/coverage.py` · `tests/unit/test_coverage_gates.py` |
| 20 | Integration with a real dependency | `tests/integration/test_repository_isolation.py` |
| 21 | Consumer-driven contract testing | `tests/contract/` · `examples/js/contract/consumer.pact.mjs` |
| 22 | End-to-end, kept thin | `examples/js/e2e/transfer.spec.mjs` |
| 23 | Flaky-test quarantine | `src/stplaybook/quality/coverage.py` (`evaluate_gates`) |
| 24 | Test data, determinism, no production data | `tests/factories.py` · `src/stplaybook/clock.py` · `src/stplaybook/config.py` |
| 25 | Coverage measures | `src/stplaybook/quality/coverage.py` |

---

## Part 3 — Security-first testing

| Slide | Topic | Implemented in |
|---|---|---|
| 28 | STRIDE threat modelling | `tests/security/test_abuse_cases.py` (each test names its threat) |
| 29 | Threat → executable test | `tests/security/test_abuse_cases.py` |
| 31 | ASVS as the test oracle | `docs/security.md` (requirement→test trace) |
| 32 | Scanning stack and its blind spots | `docs/security.md` · `src/stplaybook/authz/` |
| 33 | Authorisation matrix (BOLA/BFLA) | `src/stplaybook/authz/` · `tests/security/test_authorisation_matrix.py` |
| 34 | Fuzzing | `tests/fuzz/` · `src/stplaybook/parsing.py` |
| 35 | SBOM, SLSA, Sigstore, VEX | `src/stplaybook/security/{sbom,vex,provenance}.py` |
| 36 | Pipeline gates | `.github/workflows/ci.yml` · `Makefile` |

---

## Part 4 — Non-functional and production

| Slide | Topic | Implemented in |
|---|---|---|
| 40 | SLO-driven performance testing | `src/stplaybook/slo.py` · `examples/js/perf/transfer-slo.mjs` |

---

## Part 5 — Evaluation and governance

| Slide | Topic | Implemented in |
|---|---|---|
| 46 | NIST SSDF practice groups | `docs/governance.md` |
| 47 | KEV → EPSS → reachability → exposure | `src/stplaybook/security/triage.py` · `tests/security/test_triage.py` |
| 50 | Evidence pack | `docs/governance.md` |

---

## Corrections

Twelve findings from the Phase A critical analysis. Each is implemented, tested,
and traceable to the test that proves the corrected behaviour.

### C1 · Slide 15 — a daily limit that was really a per-transaction cap

**As shown.** An account with a ₦200,000 *daily* limit, a single transfer of
₦200,001, expecting `DailyLimitExceeded`.

**Issue.** The transfer breaches the limit only because prior spend happens to be
zero. As printed, the test verifies a per-transaction cap while claiming to
verify a cumulative daily one — the accumulation is never exercised.

**Correction.** `Account` tracks cumulative spend per UTC calendar day against an
injected clock. The slide's example is preserved verbatim as the first test;
`test_daily_limit_is_cumulative_not_per_transaction` and
`test_daily_limit_resets_on_the_next_calendar_day` exercise the rule the slide
actually describes.

### C2 · Slide 15 — ambiguous monetary unit

**As shown.** `Naira(500_000)`, with no statement of whether the argument is
naira or kobo.

**Correction.** Fixed by the type: the constructor takes **naira**, the internal
representation is integer **kobo**, and `Naira.from_kobo()` exists for the other
direction. No float ever touches an amount. `to_naira_int()` refuses to
silently discard kobo at the API boundary.

### C3 · Slide 18 — coupled generation strategies

**As shown.** `@given(st.lists(...))`, then `total = sum(amounts)` and
`parties = len(amounts)`.

**Issue.** Both parameters derive from one generated list, so party count is
bounded by list length and total correlates with parties. The search space is far
narrower than it appears.

**Correction.** `total` and `parties` are independent strategies. `parties < 1`
raises the named `InvalidPartyCount` rather than being excluded by `min_size`.

### C4 · Slide 18 — an unstated algorithm

**As shown.** `assert max(shares) - min(shares) <= 1` presented as a property of
"splitting a bill".

**Issue.** True only under largest-remainder allocation over an indivisible minor
unit. Not a general property.

**Correction.** `split_bill` implements largest remainder explicitly and says so
in its docstring, so the property is a claim about a specified algorithm.

### C5 · Slide 19 — an incomplete mutation-score formula

**As shown.** `killed ÷ (killed + survived)`.

**Issue.** Real tools also emit timeouts, no-coverage and compile errors. Whether
timeouts count as killed is a tool convention that moves the number materially —
for the repository's own worked example, 74.2% versus 70.1%.

**Correction.** `mutation_score()` takes a documented
`count_timeouts_as_killed` flag (default `True`, the Stryker/PIT convention), and
excludes no-coverage mutants from the denominator because that is diff
coverage's question, not the mutation score's.
`test_timeout_convention_moves_the_mutation_score_materially` pins both numbers.

### C6 · Slide 20 — code that would not execute

**As shown.** `repo.load(invoice_id, tenant="B")`.

**Issue.** `invoice_id` is never bound; `repo.save(...)`'s return value is
discarded. As printed this raises `NameError`.

**Correction.** The saved invoice is captured and `saved.id` used.

### C7 · Slide 20 — Docker in the default path

**Issue.** A session-scoped Testcontainers fixture makes the entire suite depend
on a container runtime, contradicting the offline-first requirement.

**Correction.** The in-memory repository is the default; the Postgres path
carries `@pytest.mark.postgres`, applies identical assertions, and skips unless
`STP_USE_POSTGRES=1`.

### C8 · Slide 21 — Pact v2 matchers in a v3 builder

**As shown.** `term({ matcher: "NGN|USD", generate: "NGN" })`.

**Issue.** Object-argument `term()` is the Pact JS **v2** DSL. The `PactV3`
builder shown around it requires `MatchersV3.regex(matcher, generate)`. Mixing
them throws at runtime.

**Correction.** `examples/js/contract/consumer.pact.mjs` uses `MatchersV3` and
names the major version in its header.

### C9 · Slide 21 — a builder chain that writes nothing

**Issue.** `PactV3` only produces a pact file when `.executeTest()` runs. As
printed, no pact is ever written.

**Correction.** `.executeTest()` is supplied, with real assertions against the
mock server.

### C10 · Slide 33 — a denial assertion that permits the disclosure it guards

**As shown.** `assert response.status_code in (401, 404)` for every denied case.

**Issue.** Collapses two distinct outcomes. The assertion passes if an anonymous
caller receives a resource-confirming 404, or if an authenticated outsider
receives a 401 revealing the resource exists elsewhere.

**Correction.** `authz/policy.py` defines `DENIED_STATUS` per principal — 401 for
anonymous, 404 for everyone else — and the matrix test asserts the exact status.
A companion test asserts the resource identifier appears in no denied response.

### C11 · Slide 34 — a fuzzer with no coverage feedback

**As shown.** `atheris.Setup(...)` and `atheris.Fuzz()`.

**Issue.** Without `atheris.instrument_imports()` around the subject import, the
fuzzer receives no coverage signal and degrades to random input generation —
losing the property that makes coverage-guided fuzzing worth running.

**Correction.** `tests/fuzz/fuzz_statement_parser.py` instruments the import, and
strengthens the oracle beyond "does not crash" to the parser's full contract.

### C12 · Slide 40 — a vacuous threshold

**As shown.** `checks: ["rate>0.99"]` in a script with no `export default
function`.

**Issue.** No `check()` calls means no samples; an empty threshold source passes
vacuously, so the gate measures nothing.

**Correction.** `examples/js/perf/transfer-slo.mjs` supplies a real default
function with `check()` calls. In Python, `evaluate_thresholds([], [...])`
returns **failing**, and
`test_a_threshold_with_no_samples_fails_rather_than_passing_vacuously` pins it.

---

## Verified without change

Four claims were checked and stand as presented.

| Slide | Claim | Verification |
|---|---|---|
| 14 | Pyramid ratios 55 / 25 / 15 / 5 | Sum to 100 |
| 22 | ₦500,000 − ₦50,000 = ₦450,000 | `test_subtraction_matches_the_slide_22_arithmetic` |
| 30 | Top 10:2025 categories, SSRF folded into A01, A09 renamed, A10 new | Against the published 2025 list |
| 31 | ASVS 5.0.0, ~350 requirements, 17 chapters, L1/L2/L3 ≈ 20/50/30% | Sum to 100; matches the released version |

---

## Repository-level deviations

Beyond the slide corrections, nine structural decisions differ from a literal
transcription. They are listed in full in the Phase A plan; in summary:

| # | Deviation | Rationale |
|---|---|---|
| D1 | Cumulative rather than per-transaction daily limit | C1 |
| D2 | Postgres integration is opt-in | Offline-first is absolute |
| D3 | Contract verification in pure Python | Keeps the default suite network-free |
| D4 | Pact, Playwright and k6 in `examples/`, not `tests/` | Keeps Node out of the gates |
| D5 | Exact per-principal denial statuses | C10 |
| D6 | Only SHA-pinnable actions are used in CI | Real SHAs, not decorative ones |
| D7 | `split_bill(total, parties)` takes explicit arguments | C3 |
| D8 | `count_timeouts_as_killed` is explicit | C5 |
| D9 | Ruff rule `N818` disabled | Exception names follow the deck verbatim (`DailyLimitExceeded`, `TenantMismatch`, `InvalidStatement`); appending "Error" to each would break slide fidelity for no readability gain |
