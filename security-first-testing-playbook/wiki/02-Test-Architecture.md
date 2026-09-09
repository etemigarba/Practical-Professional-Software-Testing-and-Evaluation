# 02 · Test Architecture

A test suite is a system with its own architecture. Get the shape wrong and it
becomes slow, flaky and distrusted — at which point developers route around it
and the whole investment is lost.

## The shape

| Level | Share | Speed | Question it answers |
|---|---|---|---|
| End-to-end | 5% | minutes | Can a real user complete the critical journey? |
| Integration | 15% | seconds | Does the wiring work against the real thing? |
| Contract / API | 25% | sub-second | Does the boundary still hold? |
| Unit | 55% | milliseconds | Is this logic right? |

Two numbers matter more than the ratio: **median pull-request pipeline duration**
and **percentage of suite runtime spent end-to-end**. A six-minute pipeline trains
a team to add tests; a forty-five minute one trains them to skip.

## FIRST and Arrange–Act–Assert

**F**ast · **I**solated · **R**epeatable · **S**elf-validating · **T**imely.

```python
def test_transfer_rejects_amount_above_daily_limit(account: Account) -> None:
    # Arrange — the smallest world in which the rule is meaningful
    # Act — exactly one call
    with pytest.raises(DailyLimitExceeded) as err:
        account.transfer(to="0123456789", amount=Naira(200_001))

    # Assert — on the observable contract, not the implementation
    assert err.value.limit == Naira(200_000)
    assert account.balance == Naira(500_000)   # nothing was mutated
```

Note the named exception carrying structured attributes, and the second assertion
proving atomicity. Both are easy to omit and both are the point.

## Assertions that actually assert

Machine-generated suites raise coverage almost for free. Coverage without
meaningful assertions is a false signal, and it is now the common failure mode.

`tests/unit/test_assertion_craft.py` proves the difference rather than asserting
it — the weak assertions genuinely do hold against a broken response:

```python
BROKEN = Response(500, {"tenantId": "tenant-b", "total": -1, "status": "PAID"})

assert BROKEN is not None     # passes
assert BROKEN.status          # passes: 500 is truthy
assert BROKEN.body is not None  # passes
```

Three rules: assert **values** not truthiness; assert **outcomes** not
interactions; always assert the **security-relevant field** — tenant, owner, role,
scope are what an attacker manipulates.

## Test doubles

Dummy · Stub · Spy · Mock · Fake.

Prefer a **fake** over a mock, and a real dependency in a container over a fake.
Every layer of pretence is a layer where production and test can quietly
disagree. A spy is legitimate when the call itself is the outcome — an audit
trail's whole purpose is that the call happened.

## Property-based testing

State the invariant; let the machine hunt.

```python
@given(total_kobo=kobo_amounts, parties=party_counts)
def test_split_bill_never_loses_or_invents_a_kobo(total_kobo, parties) -> None:
    shares = split_bill(Naira.from_kobo(total_kobo), parties=parties)
    assert sum(s.kobo for s in shares) == total_kobo
```

**Shrinking is the feature.** On failure the framework reduces the input to the
smallest case that still fails, so the report is a one-line reproduction.

**Pin every counterexample.** When a property fails, add the shrunk case as a
permanent example-based test. The property finds it once; the example keeps it
fixed. `test_pinned_single_party_receives_the_entire_total` is one such.

## Mutation testing

The only honest audit of a test suite. It changes production code on purpose and
asks whether any test noticed.

```python
from stplaybook.quality.coverage import MutationOutcome, mutation_score

outcome = MutationOutcome(killed=68, survived=25, timed_out=4, no_coverage=10)
mutation_score(outcome)                                # 74.2
mutation_score(outcome, count_timeouts_as_killed=False)  # 70.1
```

Those two numbers are the same run. Whether timeouts count as killed is a
tool convention that moves the score materially, which is why it is an explicit
flag here rather than the single formula the slide gives.

Targets: ≥ 70% in critical-band modules, ≥ 60% elsewhere, reported **per module**
— a project-wide average hides the modules that matter. Run it nightly; it is
expensive by construction.

## Contract testing

A schema says what *may* be sent; a pact says what this consumer actually
*depends on*, which is what tells you where you are free to change.

The pact here also pins the error shape and a `forbiddenFields` list, so an
over-sharing response breaks the provider's build rather than reaching a
consumer.

## Flakiness

Detect → **quarantine** → diagnose → fix or delete.

Quarantine decouples unblocking the team from diagnosing the flake. Teams that
insist on diagnosing first pay twice.

Do not **skip** — you lose the signal and the failure history. Do not paper over
with **automatic retries** — they hide the race conditions that will recur in
production, and normalise unreliability until red stops meaning anything.

Target below 1%. Above 5%, trust in the pipeline is already gone.

## Coverage

| Measure | Use | Failure mode |
|---|---|---|
| Line | Crude floor | Trivially inflated by assertion-free tests |
| Branch | Better floor | Says nothing about boundary values |
| **Diff** | **The gate: 80% of changed lines** | Ignores erosion in untouched code |
| **Mutation** | **The real quality signal** | Expensive; run nightly |
| Requirement | What assessments ask for | Needs discipline to keep traces honest |

Never set an organisation-wide line-coverage target. It is the fastest known way
to fill a repository with assertion-free tests.
