# Security Policy

## Scope and intent

This repository is teaching material. It contains **no exploit code, no offensive
tooling and no working attack payloads**. Every security example here is
defensive: a test that *detects* a weakness, never a tool that exploits one. If
you were expecting the latter, this is the wrong repository.

## Supported versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | Yes       |

## Reporting a vulnerability

Report privately through **GitHub Security Advisories** on this repository
(Security → Report a vulnerability). Please do not open a public issue for
anything you believe is exploitable.

Include, where you can: affected file and version, the behaviour you observed,
what you expected, and a minimal reproduction. A failing test is the ideal
report — it is also the form this repository argues every finding should
eventually take.

### What to expect

| Stage | Commitment |
|---|---|
| Acknowledgement | Within 5 working days |
| Initial assessment and tier | Within 10 working days |
| Fix or documented acceptance | Tracked publicly once a fix exists |

Findings are triaged with the model in `src/stplaybook/security/triage.py`: KEV
membership, then EPSS, then reachability, then asset context. The tier assigned
determines the remediation service level, and the reasoning is recorded.

## Coordinated disclosure

We ask for 90 days before public disclosure, or until a fix ships, whichever is
sooner. We will credit you unless you ask us not to.

## What this repository does not claim

* It does **not** claim an OWASP ASVS conformance level. It demonstrates how to
  test against ASVS; it has not been assessed.
* Provenance verification here is **offline**: digest, builder allow-list and
  source URI. It performs no signature cryptography and no transparency-log
  lookup. `docs/security.md` records that boundary and what a production
  verifier must add.
* The dependency surface is deliberately empty at runtime, so the supply-chain
  risk this repository carries is its toolchain, not its imports.
