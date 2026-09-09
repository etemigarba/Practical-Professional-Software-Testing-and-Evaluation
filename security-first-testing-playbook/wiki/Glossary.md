# Glossary

Terms and acronyms used across the deck and this repository.

## Testing

**AAA** — Arrange, Act, Assert. The three-part shape of a readable test.

**Assertion-free test** — a test that executes code without verifying anything
about the result. Raises coverage; proves nothing. Detected here by
`stplaybook.quality.test_auditor`.

**Contract test** — verifies that a boundary between two services still holds.
Unlike a schema, a pact records what a consumer *actually depends on*.

**Diff coverage** — the percentage of *changed* lines a test executed. The
coverage measure worth gating on.

**Fake** — a working lightweight implementation of a collaborator. Preferred over
a mock, because it can be tested against the real contract.

**FIRST** — Fast, Isolated, Repeatable, Self-validating, Timely.

**Flaky test** — passes and fails on the same commit. Worse than no test: it
teaches the team to ignore red.

**Fuzzing** — feeding generated inputs to find crashes, hangs and logic faults. A
*coverage-guided* fuzzer keeps inputs that reach new code paths.

**Mutation score** — the percentage of deliberately introduced faults that a test
suite detected. The honest audit of a suite's value.

**Mutation testing** — changing production code on purpose to see whether any
test notices.

**Property-based testing** — stating an invariant and letting a framework search
for a counterexample. On failure it **shrinks** the input to the smallest failing
case.

**Quarantine** — removing a flaky test from required checks while keeping it
running and recording. Unblocks the team without losing the signal.

**Test double** — any stand-in for a real collaborator: dummy, stub, spy, mock or
fake.

## Security

**ASVS** — OWASP Application Security Verification Standard. Version 5.0.0 (May
2025): ~350 requirements across 17 chapters at levels L1, L2 and L3.

**Abuse case** — a scenario describing how a system may be misused, written so it
can become a test.

**BOLA / BFLA** — Broken Object-Level / Function-Level Authorisation. The most
exploited patterns in API-heavy systems.

**CVSS** — Common Vulnerability Scoring System. Measures severity, **not**
likelihood of exploitation.

**DAST** — Dynamic Application Security Testing. Probes the running application.

**EPSS** — Exploit Prediction Scoring System. A daily-updated probability of
exploitation within thirty days.

**IAST** — Interactive Application Security Testing. Instruments execution during
the test run.

**KEV** — CISA's Known Exploited Vulnerabilities catalogue. Confirmed
exploitation in the wild, verified by a human.

**SAST** — Static Application Security Testing. Analyses source and data flow.

**SCA** — Software Composition Analysis. Checks dependencies against advisory
databases.

**STRIDE** — Spoofing, Tampering, Repudiation, Information disclosure, Denial of
service, Elevation of privilege.

**Threat model** — a structured answer to: what are we building, what can go
wrong, what will we do about it, did we do a good enough job?

## Supply chain

**CycloneDX** — an SBOM format oriented toward security tooling.

**in-toto** — the attestation framework whose Statement format carries SLSA
provenance.

**Provenance** — a signed record of how an artefact was built: builder, source
commit, inputs.

**SBOM** — Software Bill of Materials. What is inside a build. Generate it at
**build** time, when the dependency graph is resolved.

**Sigstore** — keyless signing with short-lived certificates bound to an OIDC
identity, recorded in a public transparency log.

**SLSA** — Supply-chain Levels for Software Artifacts. Build levels L1–L3 of
increasing provenance assurance.

**SPDX** — an SBOM format oriented toward licence compliance.

**VEX** — Vulnerability Exploitability eXchange. A producer's assertion that a
CVE is or is not exploitable in *this* product.

## Governance

**DORA metrics** — deployment frequency, lead time for changes, change failure
rate, failed deployment recovery time, and rework rate.

**Evidence pack** — the artefacts an assessor asks for. Should fall out of the
pipeline, not be assembled by hand.

**ISO/IEC 25010:2023** — the product quality model. Nine characteristics; the
2023 revision added Safety.

**ISO/IEC/IEEE 29119** — the software testing standard: concepts, processes,
documentation, techniques, keyword-driven testing.

**SSDF** — NIST SP 800-218 Secure Software Development Framework. Four practice
groups: PO, PS, PW, RV.

**WCAG 2.2** — Web Content Accessibility Guidelines. Level AA is the common
procurement target.

## Nigerian context

**CBN** — Central Bank of Nigeria.

**GAID 2025** — the NDPC's General Application and Implementation Directive under
the NDPA.

**Kobo** — the minor unit of the Naira. 100 kobo = ₦1. Amounts here are stored as
integer kobo so no float ever touches money.

**NDPA 2023** — Nigeria Data Protection Act. Governs processing of personal data,
including in test environments.

**NDPC** — Nigeria Data Protection Commission.

**NUBAN** — Nigeria Uniform Bank Account Number. Ten digits, the last a check
digit computed over the bank code and serial.

**₦ (Naira)** — the currency used throughout the examples.
