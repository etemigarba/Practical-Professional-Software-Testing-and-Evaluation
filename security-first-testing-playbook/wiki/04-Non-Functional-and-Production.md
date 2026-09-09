# 04 · Non-Functional and Production Testing

Functional correctness is the easy half. Systems fail in production because of
latency under load, a dependency that never returned, a screen reader that could
not read a label, or a change nobody could observe going wrong.

## Performance against objectives, not feelings

"Acceptable performance" is unfalsifiable. A service-level objective is a number,
a percentile, a load profile and a window.

```python
from stplaybook.slo import evaluate_thresholds

for result in evaluate_thresholds(samples, ["p(95)<250", "p(99)<800"]):
    print(result.describe())     # PASS p(95)<250 (observed 211.40)
```

**Report percentiles, never means.** A p50 of 42 ms alongside a p99.9 of 1,850 ms
averages to something that describes nobody's experience.

Percentiles here are **nearest rank**, stated explicitly — an unstated percentile
definition makes a reported number unreproducible.

### A threshold with no samples fails

```python
evaluate_thresholds([], ["p(95)<250"])[0].passed   # False
```

This is deliberate. A k6 `checks` threshold declared in a script with no
`check()` calls has no source, and an empty source passes vacuously — a gate
measuring nothing. Refusing to pass is the honest behaviour.

### Four kinds of load test

| | Purpose |
|---|---|
| Load | Expected peak, sustained. Confirms the objective holds |
| Stress | Past the limit. Finds where it breaks and whether it breaks safely |
| Soak | Hours at steady load. Finds leaks, exhaustion and drift |
| Spike | Instantaneous surge. Tests autoscaling and load shedding |

Compare against the **previous release**, not against an absolute that drifts.

## Chaos engineering

A chaos experiment has a hypothesis, a blast radius, a stop condition and a
rollback. Without those four it is simply an incident you caused.

1. **Steady state** — define the metric that means "working": successful
   checkouts per minute, not CPU.
2. **Hypothesise** — "if payments returns 500 for 60 s, checkout degrades but
   does not fail."
3. **Inject** — smallest blast radius first: one instance, one region, off-peak,
   with a stop button.
4. **Measure and fix** — every surprise becomes a test and a runbook entry.

Prove **graceful degradation**: read-only mode beats an error page, a cached
price beats no price.

**Recovery drills** are the most commonly skipped and most consequential.
Restore a backup, fail over the database, rotate a credential — timed, scheduled,
recorded. An untested backup is a hypothesis.

## Accessibility

WCAG 2.2 Level AA is the working target in most procurement and public-sector
contexts. Automated scanning detects roughly **a third** of the success criteria
— claiming compliance from a clean automated run is not defensible.

Automate on every pull request: contrast, alternative text, form labels, ARIA
misuse, heading order, landmarks. Verify by hand every release: keyboard-only
traversal with visible focus, a screen-reader pass, target size and dragging
alternatives (new in 2.2), and whether alternative text is *useful* rather than
merely present.

ISO/IEC 25010:2023 lists accessibility under **interaction capability** — a
quality characteristic, not a compliance chore.

## Observability-driven testing

Some properties only exist under real traffic. Observe them deliberately rather
than discovering them from a customer.

* **Synthetic monitoring** — critical journeys executed against production on a
  schedule from multiple regions. Catches DNS, TLS, certificate and routing
  faults no unit test can see.
* **Instrument for testability** — if you cannot answer "did that work?" from
  telemetry, the feature is not finished.
* **Alert on symptoms, not causes** — page on user-visible objective breaches;
  CPU belongs on a dashboard, not a pager.
* **Security telemetry is testable too** — OWASP A09 exists because logs nobody
  acts on have almost no value. Trigger an authorisation failure and assert the
  alert fires.

## Progressive delivery

Dark launch → internal cohort → canary → progressive → full with the flag
retained.

**Automate the rollback trigger.** The canary analysis decides, not a human:
"error rate exceeds control by 0.5 points for two minutes → revert" removes
hesitation from the worst possible moment for it.

**Give every flag an expiry date.** Flags are branches in production, and each
one doubles the configuration space your tests must cover. Fail the build when a
flag outlives its date.

**Decouple deploy from release.** Then a rollback is a configuration change
measured in seconds rather than a redeployment measured in minutes.

Every stage above is a test. The difference from a pre-production suite is that
the subject is real traffic and the assertion is a telemetry comparison against a
control group.
