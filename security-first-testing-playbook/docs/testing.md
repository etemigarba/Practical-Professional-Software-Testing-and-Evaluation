# Testing Guide

## Running the suites

```bash
pip install -e ".[dev]"
pytest                    # everything; no Docker, no network, ~1 second
make verify               # lint + typecheck + test + audit — the CI gate
```

| Suite | Command | Default |
|---|---|---|
| Unit | `pytest tests/unit` | runs |
| Property | `pytest tests/property` | runs |
| Contract | `pytest tests/contract` | runs |
| Security | `pytest tests/security` | runs |
| Integration | `pytest tests/integration` | in-memory; Postgres skipped |
| Fuzz corpus replay | `pytest tests/fuzz` | runs |
| Live fuzzing | `make fuzz` | opt-in |
| Mutation | `make mutation` | nightly |

## The opt-in suites

```bash
# Real Postgres (slide 20). Needs a container runtime.
pip install -e ".[postgres]"
STP_USE_POSTGRES=1 pytest tests/integration

# Coverage-guided fuzzing (slide 34).
pip install -e ".[fuzz]"
STP_ENABLE_FUZZ=1 python tests/fuzz/fuzz_statement_parser.py -atheris_runs=200000

# Mutation testing (slide 19). Expensive by construction.
pip install -e ".[mutation]"
make mutation
```

Each skips cleanly when its dependency is absent, so a fresh clone never fails
for a reason the reader did not choose.

## What each level is responsible for

Slide 14's argument is that levels answer different questions, and an assertion
belongs at the lowest level that can answer its question.

| Level | Question | Example here |
|---|---|---|
| Unit | Is this logic right? | `test_daily_limit_is_cumulative_not_per_transaction` |
| Property | Does the invariant hold across the whole input space? | `test_split_bill_never_loses_or_invents_a_kobo` |
| Contract | Does the boundary still hold? | `test_response_omits_every_forbidden_field` |
| Integration | Does the wiring work against the real thing? | `test_repository_enforces_tenant_isolation` |
| Security | Can somebody do what they should not? | `test_invoice_authorisation_matrix` |
| Fuzz | What did nobody think to try? | `fuzz_statement_parser.py` |

## Writing a test in this repository

### One reason to fail

```python
def test_transfer_rejects_amount_above_daily_limit(account: Account) -> None:
    # Arrange — the fixture is the smallest world in which the rule is meaningful
    # Act — exactly one call
    with pytest.raises(DailyLimitExceeded) as err:
        account.transfer(to="0123456789", amount=Naira(200_001))

    # Assert — on the observable contract, not the implementation
    assert err.value.limit == Naira(200_000)
    assert account.balance == Naira(500_000)   # nothing was mutated
```

The second assertion is the one people leave out. It proves the operation was
atomic — that the rejection did not half-happen.

### Assert values, not truthiness

`tests/unit/test_assertion_craft.py` demonstrates the difference by proving that
weak assertions genuinely do hold against a broken response:

```python
BROKEN = Response(500, {"tenantId": "tenant-b", "total": -1, "status": "PAID"})

def test_weak_assertions_hold_even_against_a_broken_response() -> None:
    assert BROKEN is not None
    assert BROKEN.status          # 500 is truthy
    assert BROKEN.body is not None
```

Every one of those passes. That is the point.

### Assert on what is *not* returned

Absence assertions are where disclosure bugs are caught:

```python
assert invoice.id not in response.text
assert response.body is None
```

### Enumerate, do not sample

The authorisation matrix is generated from the policy, so adding a role or an
operation grows the test count automatically:

```python
MATRIX = enumerate_matrix()          # 4 principals × 3 operations = 12 cases

@pytest.mark.parametrize("case", MATRIX, ids=lambda c: c.id)
def test_invoice_authorisation_matrix(case, repository, api, rng): ...
```

A coverage gap becomes a failing test rather than an oversight nobody noticed.

## The self-referential gate

`make audit` runs the assertion-free-test detector over this repository's own
suite, and CI fails if it finds anything:

```
Audited 113 test(s) under tests
No assertion-free tests found.
```

A repository that argues against assertion-free tests must not contain one.

### On the auditor's weak-test reports

The auditor currently reports four tests as *weak* — those asserting a domain
predicate directly, such as `assert is_valid_nuban(number, "058")`. That is a
false positive: the predicate is meaningful. It has been left uncorrected rather
than worked around, because gaming your own detector to produce a clean report
is precisely the behaviour the detector exists to discourage. Weak findings are
reported; only assertion-free findings fail the build.

## Coverage

```bash
make coverage
```

Gate on **diff coverage** (80% of changed lines) and **mutation score** (70% in
the critical band). Report line coverage as context. Never set an
organisation-wide line-coverage target — slide 25 and hard experience agree that
it is the fastest route to a repository full of assertion-free tests.

## Flakiness

Target below 1%. Above 5%, trust in the pipeline is already gone.

When a test flakes: quarantine it (remove it from required checks, keep it
running and recording), give it an owner and an expiry date, then diagnose.
Do not skip it — skipping loses both the signal and the failure history that
would tell you whether it is resolving. Do not paper over it with automatic
retries, which hide the race conditions that will recur in production.

`evaluate_gates()` encodes both thresholds, and the release gate requires zero
quarantined tests in the critical band.
