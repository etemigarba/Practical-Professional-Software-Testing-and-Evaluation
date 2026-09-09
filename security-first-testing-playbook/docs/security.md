# Security Guide

## The claim this repository makes, and the ones it does not

**It demonstrates** how to test against OWASP ASVS, how to turn STRIDE threats
into executable regression tests, how to triage findings by exploitability
rather than by severity, and how to verify what you shipped.

**It does not claim** an ASVS conformance level, a certification, or a security
assessment. Slide 31's rule applies to this repository as much as to yours: a
documented partial claim is credible; an unqualified one is not.

## What no scanner will find for you

Slide 32's table, and the reason `src/stplaybook/authz/` exists.

| Tool class | Sees | Blind to |
|---|---|---|
| SAST | Injection sinks, unsafe deserialisation, hardcoded secrets | Runtime configuration, business logic, authorisation intent |
| SCA | Declared and transitive dependencies against advisories | Whether the vulnerable path is reachable in your code |
| Secret scanning | Credentials in code, history, CI logs | Secrets held only in a running process |
| IaC / container | Terraform, Kubernetes, Dockerfile misconfiguration | Drift after deployment |
| DAST | The running application: headers, TLS, injection | Anything behind authentication it cannot reach; logic flaws |
| IAST | Instrumented execution, fewer false positives | Only the paths your tests exercise |
| Fuzzing | Crashes, hangs, parser edge cases | Semantic correctness without an oracle |

None of them finds broken access control, because none of them knows who *should*
be allowed to do what. That is why A01 has stayed at number one, and why the
authorisation matrix is written by hand — as data, in `authz/policy.py`, so it
can be enumerated, diffed and reviewed.

## Turning a threat into a test

The step most programmes skip. A threat that does not become a failing test will
be reintroduced within two releases.

| STRIDE | Abuse case | Test |
|---|---|---|
| Elevation of privilege | A user requests another tenant's invoice by guessing its id | `test_elevation_of_privilege_guessed_identifier_returns_404_not_403` |
| Information disclosure | An error reveals internal structure | `test_information_disclosure_repository_error_names_no_internals` |
| Spoofing | An unauthenticated caller reaches a destructive operation | `test_spoofing_an_unauthenticated_caller_is_stopped_before_any_read` |
| Tampering | A denied delete leaves a side effect | `test_tampering_deleting_another_tenants_invoice_changes_nothing` |
| Tampering | An artefact is swapped between build and deploy | `test_a_tampered_artefact_is_rejected_on_digest` |

Each was first seen to fail against a vulnerable version. A security test that
has never been observed to fail is an assumption, not a control.

## 404, never 403

The single most consequential decision in `invoicing.py`.

```python
DENIED_STATUS = {
    "anonymous":          401,   # "identify yourself" discloses nothing
    "same_tenant_viewer": 404,   # everyone else: existence is itself a secret
    "other_tenant_admin": 404,
    "owner":              404,
}
```

A 403 with a body confirms the resource exists. `InvoiceNotFound` and
`TenantMismatch` are distinct internally — logs and logic keep the difference —
and identical at the boundary.

Slide 33 asserts `status in (401, 404)`, which passes even when this control is
broken in either direction. Correction C10 pins each status exactly.

## Supply chain: four artefacts, four questions

| Artefact | Question | Module |
|---|---|---|
| SBOM | What is inside? | `security/sbom.py` |
| SLSA provenance | How was it built? | `security/provenance.py` |
| Sigstore signature | Who vouches for it? | *see limitations* |
| VEX | Which advertised CVEs actually matter here? | `security/vex.py` |

None substitutes for another. Generate the SBOM at **build** time, when the
dependency graph is fully resolved — a manifest read at development time records
intent, not what shipped. Verify provenance at **deploy** time, not merely at
publish: the window between the two is exactly where the tampering abuse case
lives.

### Limitations, stated plainly

`verify_provenance()` checks a SHA-256 digest, a builder allow-list and a source
URI. It performs **no signature cryptography and no transparency-log lookup**,
both of which require network access this repository refuses to take on by
default.

A production verifier must add: Sigstore/cosign signature verification against
the artefact, Rekor inclusion proof, certificate-identity binding to the expected
OIDC issuer and subject, and expiry checks. Use `cosign verify-attestation` for
this; do not extend the offline verifier to pretend it does more.

### VEX requires justification

Only a **justified** `not_affected` refutes a finding:

```python
@property
def refutes(self) -> bool:
    return self.status is VexStatus.NOT_AFFECTED and bool(self.justification)
```

An unjustified refutation is an opinion. `test_an_unjustified_not_affected_statement_refutes_nothing`
holds the line.

VEX **annotates**; it never deletes. A suppressed finding that leaves no trace is
indistinguishable from one nobody ever examined.

## Triage: four signals, in order

```
KEV membership          → P0, regardless of any score
VEX refuted / unreachable → P3
High EPSS + exposed      → P1
High EPSS                → P2
High CVSS + exposed      → P2
otherwise                → P3
```

KEV is a floor, not a ceiling: absence never proves safety, which is why the
remaining signals still run. KEV also outranks a producer's own VEX refutation —
confirmed exploitation in the wild beats an assertion of non-exploitability.

Slide 47's worked example is a test:
`test_high_epss_on_an_exposed_asset_outranks_a_higher_cvss` proves CVSS 7.5 at
EPSS 0.94 lands at P1 while CVSS 9.1 at EPSS 0.003 lands at P2.

## Data protection

No fixture contains real or realistic personal data. Everything in
`tests/factories.py` is generated, and no value corresponds to a real person,
account or business.

Under the Nigeria Data Protection Act 2023 and the NDPC's 2025 General
Application and Implementation Directive — as under GDPR — a copy of a production
database in a test environment is a processing activity requiring a lawful basis,
a record, and security safeguards. It turns every developer laptop into a
regulated data store. Synthesise, or de-identify irreversibly.

## Requirement-to-test trace

The three-column table an assessment asks for first. Illustrative rather than
exhaustive; extend it as you extend the suite.

| ASVS v5.0.0 area | Requirement in prose | Test |
|---|---|---|
| Authorisation | Access decisions are enforced on every request at a trusted layer | `test_invoice_authorisation_matrix` |
| Authorisation | Denials disclose nothing about resource existence | `test_denied_responses_never_disclose_the_resource` |
| Error handling | Errors reveal no internal structure | `test_information_disclosure_repository_error_names_no_internals` |
| Input validation | Untrusted input is bounded and parsed defensively | `test_arbitrary_bytes_either_parse_or_raise_invalid_statement` |
| Configuration | Configuration is validated and secrets are absent from source | `tests/unit/test_config.py` |
| Supply chain | Build integrity is verified before deployment | `test_matching_artefact_and_attestation_verify` |

Cite requirements with the version — `v5.0.0-6.2.1`, not `ASVS 6.2.1`. Numbering
changed substantially between 4.x and 5.0, so an uncited reference is ambiguous.
