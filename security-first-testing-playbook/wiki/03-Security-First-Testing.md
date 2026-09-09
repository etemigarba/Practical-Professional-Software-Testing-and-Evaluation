# 03 · Security-First Testing

Security testing is not a scanner you buy. It is a chain: model the threats, turn
each into an executable test, gate the pipeline on the result, and prove the
provenance of everything you did not write yourself.

## Shift left *and* shift right

Left of deployment you prevent; right of it you detect. A programme doing only
one is half a programme.

The measure of maturity is the **ratio**: findings caught left of deployment
versus findings reported by users, researchers or regulators.

## Threat modelling

Four questions: What are we building? What can go wrong? What are we going to do
about it? Did we do a good enough job?

STRIDE maps one-to-one onto security properties, which is what makes it testable:

| | Threat | Property |
|---|---|---|
| S | Spoofing | Authenticity |
| T | Tampering | Integrity |
| R | Repudiation | Non-repudiation |
| I | Information disclosure | Confidentiality |
| D | Denial of service | Availability |
| E | Elevation of privilege | Authorisation |

Threat-model whenever a trust boundary moves: a new integration, a new role, a
new data store, a new agent with tool access.

## From threat to test

The step most programmes skip. A threat that does not become a failing test will
be reintroduced within two releases. In `tests/security/test_abuse_cases.py`,
every test names the threat it derives from.

**Write the test so it fails against the vulnerable version first.** A security
test that has never been seen to fail is an assumption, not a control.

## OWASP Top 10:2025

Published November 2025, finalised January 2026. A01 Broken Access Control (now
explicitly covering BOLA and BFLA, with SSRF folded in) · A02 Security
Misconfiguration · **A03 Software Supply Chain Failures** (the highest debut
ever) · A04 Cryptographic Failures · A05 Injection · A06 Insecure Design · A07
Authentication Failures · A08 Software or Data Integrity Failures · A09 Security
Logging and Alerting Failures · A10 Mishandling of Exceptional Conditions.

The Top 10 is an awareness document, not a standard. **Test against ASVS; report
against the Top 10.**

## ASVS 5.0 as the test oracle

Version 5.0.0 (May 2025): roughly 350 requirements across 17 chapters, at levels
L1 (~20%), L2 (~50%, the correct default for business applications) and L3
(~30%).

Cite requirements **with the version** — `v5.0.0-6.2.1`, not `ASVS 6.2.1`.
Numbering changed substantially between 4.x and 5.0.

Maintain a three-column trace: requirement → test identifier → last result. It is
the single most requested artefact in an assessment. There is a starter table in
`docs/security.md`.

## What no scanner finds

SAST, SCA, secret scanning, IaC scanning, DAST, IAST and fuzzing each have a
characteristic blind spot, and buying more of the same category does not close
it. **None of them finds broken access control**, because none knows who *should*
be allowed to do what.

That is why A01 has stayed at number one, and why the authorisation matrix is
written by hand — as data:

```python
from stplaybook.authz import enumerate_matrix

MATRIX = enumerate_matrix()   # 4 principals × 3 operations = 12 cases
```

Add a role or an endpoint and the matrix grows automatically, so a coverage gap
becomes a failing test rather than an oversight.

### 404, never 403

```python
DENIED_STATUS = {
    "anonymous":          401,   # "identify yourself" discloses nothing
    "same_tenant_viewer": 404,
    "other_tenant_admin": 404,   # a 403 with a body confirms it exists
    "owner":              404,
}
```

Assert on **what is not returned** — no identifier, no stack trace, no internal
hostname, no other tenant's field. Absence assertions are where disclosure bugs
are caught.

## Fuzzing

Coverage-guided fuzzers mutate inputs and keep the ones reaching new code paths.
Fuzz the parsers first: anything consuming untrusted bytes.

**Give the fuzzer an oracle.** "Does not crash" is weak; "parses or raises the
declared exception, and the invariants hold" is strong and catches logic faults
as well as memory faults.

Seed the corpus and **keep it** — every crash reproducer here is committed as an
ordinary regression test, so it runs in the default suite forever after.

## Supply chain

| Artefact | Question |
|---|---|
| SBOM | What is inside? |
| SLSA provenance | How was it built? |
| Sigstore | Who vouches for it? |
| VEX | Which advertised CVEs actually matter here? |

None substitutes for another. Generate the SBOM at **build** time; verify
provenance at **deploy** time, not merely at publish — the window between the two
is where the tampering abuse case lives.

Only a **justified** `not_affected` VEX statement refutes a finding. An
unjustified refutation is an opinion. And VEX annotates rather than deletes: a
suppressed finding leaving no trace looks like one nobody examined.

## Pipeline gates

Publish what blocks and what only warns. An unwritten gate is renegotiated under
deadline pressure every time; a written one is negotiated once, in daylight. See
`docs/governance.md` for the full table.
