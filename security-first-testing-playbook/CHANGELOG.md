# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-09-07

First release. Companion codebase to the 56-slide deck *Software Testing &
Evaluation: A Security-First Playbook*.

### Added

* **Domain under test** — `Naira` value object over integer kobo, NUBAN check
  digits, a ledger with a cumulative daily limit, a tenant-scoped invoice
  repository and API, and a bounded bank-statement parser.
* **Test architecture** — unit tests in Arrange-Act-Assert form, Hypothesis
  property suites, an in-process consumer-driven contract verifier, and an
  Atheris fuzz target with a committed seed corpus and crash reproducers.
* **Security** — an exhaustively enumerated authorisation matrix, STRIDE-derived
  abuse-case tests, four-signal vulnerability triage (KEV, EPSS, reachability,
  asset context), CycloneDX SBOM parsing, CSAF VEX application, and offline
  in-toto provenance verification.
* **Quality measurement** — risk banding, diff coverage, mutation scoring with
  an explicit timeout convention, and an AST auditor that detects assertion-free
  tests.
* **Governance** — MIT licence with an explicit no-permission-required grant,
  SHA-pinned CI across three operating systems and two Python versions, a
  disclosure policy, and a nine-page wiki.

### Corrected from the slides

Twelve corrections, each recorded in `docs/slide-to-code-map.md`. The two that
would not have executed as printed: slide 20's unbound `invoice_id`, and slide
21's Pact builder with no `.executeTest()` terminator.

[1.0.0]: https://github.com/etemigarba/security-first-testing-playbook/releases/tag/v1.0.0
