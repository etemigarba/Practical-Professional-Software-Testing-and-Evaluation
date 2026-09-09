# Governance and Evidence

## NIST SSDF as the spine

NIST SP 800-218 organises secure development into four practice groups. Mapping
each to the pipeline stage that produces its evidence turns a framework into a
coverage check on your own automation.

| Group | Practice | Where the evidence comes from |
|---|---|---|
| **PO** Prepare the Organization | Security requirements defined; roles assigned; toolchains specified and secured | `docs/security.md`, `pyproject.toml`, `.github/workflows/ci.yml` |
| **PS** Protect the Software | Code protected from tampering; release integrity verifiable; releases archived | SHA-pinned actions, `security/provenance.py`, signed release tags |
| **PW** Produce Well-Secured Software | Design reviewed; secure coding; build configured securely; **code reviewed and tested (PW.7, PW.8)** | The whole of `tests/`, plus the four blocking CI gates |
| **RV** Respond to Vulnerabilities | Vulnerabilities identified, assessed, prioritised, remediated; root causes analysed | `SECURITY.md`, `security/triage.py`, `security/vex.py` |

Most testing evidence lives in **PW** and **RV**. That is the practical starting
point for anyone answering a vendor questionnaire.

## Pipeline gates

Published, so they are negotiated once in daylight rather than every time under
deadline pressure.

| Stage | Runs | Blocks when | Budget |
|---|---|---|---|
| Pre-commit | Format, lint, secret scan | A credential pattern is detected | < 5 s |
| Pull request | Unit, property, contract, integration, security; lint; types; audit | Any test fails · lint or type warning · assertion-free test | < 6 min |
| Merge to main | Full suite, SBOM generation, licence policy | Any suite fails · SBOM cannot be produced · forbidden licence | < 20 min |
| Nightly | Mutation testing, live fuzzing | **Nothing** — reported, reviewed at the sprint boundary | Unbounded |
| Deploy | Signature and provenance verification | Artefact unsigned, provenance missing, or policy denies | < 30 s |

Two rules keep gates credible. A blocking gate must be fast enough that nobody
wants it removed. Every exception must be granted by a named person with an
expiry date recorded in the pipeline.

The nightly row is deliberate. Mutation testing and fuzzing are expensive by
construction; putting them on the pull-request path would destroy the six-minute
budget and train the team to batch changes, which raises change failure rate.

## Metrics worth reporting

Report throughput, stability, quality and security **together**. Any one of them
alone can be improved by damaging the others.

| Category | Metrics |
|---|---|
| Delivery (DORA) | Deployment frequency · lead time for changes · change failure rate · failed deployment recovery time · rework rate |
| Quality | Mutation score in the critical band · diff coverage on changed lines · flakiness rate · escaped defects per release · median PR pipeline duration |
| Security | Mean time to remediate by tier · share of releases with a complete SBOM and verified provenance · findings caught left of deployment versus reported externally · ASVS requirement coverage |

### Do not measure

* **Tests written or executed per sprint** — rewards volume, and volume is now
  trivially generated.
* **Defects found per tester** — rewards finding defects late rather than
  preventing them.
* **A single organisation-wide line-coverage percentage** — the fastest known
  route to assertion-free tests.

## The evidence pack

What an assessor asks for. If producing this takes a project, the pipeline is not
instrumented; if it takes an afternoon, it is.

| Artefact | Produced by |
|---|---|
| Test strategy and risk banding | `docs/testing.md` · `quality/risk.py` |
| Requirement-to-test trace | `docs/security.md` |
| Pipeline run records | GitHub Actions run history |
| SBOM per release | `make sbom` in the `supply-chain` CI job |
| Provenance and signatures | `security/provenance.py` · `cosign verify-attestation` |
| VEX statements | `tests/golden/vex.csaf.json` as the shape |
| Vulnerability register | Triage output by tier, with owners and dates |
| Independent test reports | Penetration test findings, retest, resulting regression tests |
| Accepted risks | Each with a named accepter, justification and expiry |

Generate every one from the pipeline. Evidence assembled by hand at audit time
describes an intention rather than a practice.

A useful habit: a quarterly **evidence drill** — pick a release at random and
produce the full pack within one working day. It exposes gaps far more cheaply
than an audit does.

## The 2026 compliance map

| Instrument | Binds | Demands of testing evidence |
|---|---|---|
| EU Cyber Resilience Act (2024/2847) | Anyone placing a product with digital elements on the EU market | Reporting of actively exploited vulnerabilities and severe incidents from 11 September 2026 — 24-hour early warning, 72-hour notification. CE marking from 11 December 2027. In practice requires an SBOM and continuous vulnerability monitoring. |
| Nigeria Data Protection Act 2023 + GAID 2025 | Controllers and processors handling data of people in Nigeria | Registration for entities of major importance, documented lawful basis, impact assessments, breach notification, records of security safeguards — including in test environments. |
| NIST SP 800-218 (SSDF) | US federal suppliers by attestation; widely cited in vendor questionnaires | Evidence for PW.7, PW.8 and RV.1–RV.3. |
| PCI DSS 4.0 / ISO 27001 / SOC 2 | Payment, certified and audited organisations | Secure development lifecycle evidence, change control, vulnerability management service levels, independent testing records. |

Verify each against its primary source before quoting it in an audit or a
contract. These summaries are a starting point, not legal advice.

## Accepted risks in this repository

Stated openly, because slide 11 argues that documented accepted risk with a named
owner is a mature control and silence is not.

| Risk | Accepted because | Owner | Review |
|---|---|---|---|
| Provenance verification is offline only | Network access would break the offline-first guarantee; documented in `docs/security.md` | Maintainer | Each minor release |
| Contract verification does not use a Pact broker | Same; the real DSL is preserved in `examples/js/` | Maintainer | Each minor release |
| Four tests report as *weak* under our own auditor | They assert domain predicates; gaming the detector would be worse than the false positive | Maintainer | Each minor release |
| No ASVS level is claimed | The repository has not been assessed | Maintainer | On assessment |
