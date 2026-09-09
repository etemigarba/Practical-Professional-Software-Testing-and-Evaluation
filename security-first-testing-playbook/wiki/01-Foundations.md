# 01 · Foundations

## Verification, validation, evaluation

Three different questions. Teams that conflate them ship correct software nobody
wanted.

| | Question | Who answers it |
|---|---|---|
| **Verification** | Did we build the product right? | The team, mostly automatically |
| **Validation** | Did we build the right product? | The user, or their proxy |
| **Evaluation** | How good is it, on what evidence? | A regulator, customer or board |

Security testing spans all three: does the control work, is it the right control
for this threat, and can we demonstrate it to a third party?

## ISO/IEC 25010:2023

Nine product-quality characteristics. The 2023 revision added **Safety**, and
renamed Usability → *Interaction capability* and Portability → *Flexibility*.

Functional suitability · Performance efficiency · Compatibility · Interaction
capability · Reliability · **Security** · Maintainability · Flexibility · Safety

Security is a first-class characteristic, not an afterthought: confidentiality,
integrity, non-repudiation, accountability, authenticity, and resistance.

Use it as a requirements checklist, not decoration. For each characteristic:
*what is our target, how is it measured, and which test proves it?*

## ISO/IEC/IEEE 29119

Five parts: concepts, processes, documentation, techniques, and keyword-driven
testing. Adopt the **vocabulary and artefact names** even if you keep them
lightweight. A one-page test strategy using standard headings survives an audit;
a wiki page called "how we test" does not.

## Risk-based testing

Exhaustive testing is impossible, so uniform testing is always the wrong
allocation. `src/stplaybook/quality/risk.py` makes the banding computable:

```python
from stplaybook.quality.risk import assess, Impact, Likelihood

assessment = assess("payment authorisation", Impact.SEVERE, Likelihood.LIKELY)
assessment.band                  # Band.CRITICAL
assessment.required_techniques   # includes PENETRATION_TEST
assessment.release_rule          # "No known critical or high findings."
assessment.rationale             # "impact=severe x likelihood=likely (score 12) -> critical"
```

Impact dominates deliberately: a severe-impact component is never banded below
high however rarely it is expected to fail, because the cost of being wrong about
likelihood is asymmetric.

**Record the reasoning, not just the verdict.** When an incident happens, the
question asked is "why was this rated medium?" — and `rationale` is the answer.

| Band | Required depth | Release rule |
|---|---|---|
| Critical | Unit + property + mutation + contract + SAST/SCA + DAST + pen test | No known critical or high findings |
| High | Unit + integration + contract + SAST/SCA | No known critical findings |
| Medium | Unit + integration | Documented acceptance |
| Low | Smoke tests | Team discretion |

## The test strategy

Nine sections, one page each: scope and risk banding · test levels and types ·
security requirements · environments and data · automation and tooling · entry
and exit criteria · defect management · metrics and reporting · **risks and
exceptions**.

Section nine is the one teams omit and auditors look for first. Accepted risk
with a named owner and an expiry date is a mature control; silence is not. This
repository states its own in `docs/governance.md`.

## Enforceable exit criteria

A gate that cannot be evaluated mechanically is not a gate — it is a
conversation.

| Weak | Enforceable |
|---|---|
| "All critical tests pass" | Full suite green; zero quarantined tests in the critical band |
| "Coverage is adequate" | Diff coverage ≥ 80% on changed lines; mutation score ≥ 70% |
| "Security review completed" | Zero open findings at the targeted ASVS level; SAST and SCA green |
| "Performance is acceptable" | p95 within 10% of the previous release under the standard profile |

`evaluate_gates()` in `quality/coverage.py` implements the right-hand column, and
reports **every** breach rather than short-circuiting on the first — a gate that
reveals one problem per run trains a team to fix one problem per run.
