# 05 · Evaluation and Governance

Evaluation is forming a defensible judgement about software on stated evidence —
for a board, a customer, an auditor or a regulator. In 2026 that judgement is
increasingly a legal obligation rather than a courtesy.

## NIST SSDF (SP 800-218)

| Group | Concern |
|---|---|
| **PO** Prepare the Organization | Requirements, roles, toolchains, secured development environment |
| **PS** Protect the Software | Code protected from tampering; release integrity verifiable; releases archived |
| **PW** Produce Well-Secured Software | Design review, secure coding, secure build, **code review and testing (PW.7, PW.8)** |
| **RV** Respond to Vulnerabilities | Identify, assess, prioritise, remediate; analyse root causes |

Most testing evidence lives in **PW** and **RV**. Map each practice to the
pipeline stage producing its evidence and the framework stops being paperwork —
it becomes a coverage check on your own automation.

## Vulnerability triage

Patching by CVSS severity alone means patching almost everything, which in
practice means patching late. Four signals, in precedence order:

```python
from stplaybook.security.triage import triage, Finding

triage(Finding("CVE-2026-0002", "libbar", cvss=7.5, epss=0.94, internet_facing=True)).tier
# Tier.P1
triage(Finding("CVE-2026-0003", "libbaz", cvss=9.1, epss=0.003, internet_facing=True)).tier
# Tier.P2
```

A CVSS 7.5 at EPSS 0.94 **outranks** a CVSS 9.1 at EPSS 0.003.

1. **KEV** — confirmed exploitation in the wild. Emergency regardless of score. A
   floor, not a ceiling: absence never proves safety.
2. **EPSS** — probability of exploitation within thirty days.
3. **Reachability** — including a published VEX refutation. A vulnerable function
   nothing calls is a documentation task, not an incident.
4. **Asset context** — exposure and data sensitivity. The one signal no external
   score can supply.

| Tier | Service level |
|---|---|
| P0 | Emergency change; hours |
| P1 | Days; tracked daily |
| P2 | Next scheduled release |
| P3 | Documented; reviewed quarterly |

This ordering typically halves an unmanageable queue while raising the share of
genuinely exploitable issues fixed.

## Metrics

Report throughput, stability, quality and security **together**. Any one alone
can be improved by damaging the others.

**Delivery (DORA, five metrics):** deployment frequency · lead time for changes ·
change failure rate · failed deployment recovery time · rework rate. Read them
together — a team can now be fast and unstable at once.

**Quality:** mutation score in the critical band · diff coverage · flakiness rate
· escaped defects · median PR pipeline duration.

**Security:** mean time to remediate by tier · share of releases with complete
SBOM and verified provenance · findings caught left of deployment versus reported
externally · ASVS requirement coverage.

### Do not measure

Tests written per sprint (rewards volume, and volume is trivially generated) ·
defects found per tester (rewards finding late rather than preventing) · a single
organisation-wide line-coverage percentage (the fastest route to assertion-free
tests).

## The 2026 compliance map

| Instrument | Demands |
|---|---|
| **EU Cyber Resilience Act** (2024/2847) | Reporting of actively exploited vulnerabilities from **11 September 2026** — 24-hour early warning, 72-hour notification. CE marking from 11 December 2027. In practice: an SBOM per release and continuous monitoring. |
| **Nigeria Data Protection Act 2023 + GAID 2025** | Registration for entities of major importance, documented lawful basis, impact assessments, breach notification, records of safeguards — including in test environments. |
| **NIST SP 800-218** | Evidence for PW.7, PW.8, RV.1–RV.3. |
| **PCI DSS 4.0 / ISO 27001 / SOC 2** | Secure development lifecycle evidence, change control, remediation service levels, independent testing records. |

Verify each against its primary source before quoting it in an audit or contract.

## The evidence pack

Test strategy and risk banding · requirement-to-test trace · pipeline run records
· SBOM per release · provenance and signatures · VEX statements · vulnerability
register · independent test reports · **accepted risks, each with a named
accepter and an expiry date**.

Generate every one from the pipeline. Evidence assembled by hand at audit time
describes an intention rather than a practice.

Try a quarterly **evidence drill**: pick a release at random, produce the full
pack within one working day. It exposes gaps far more cheaply than an audit does.
