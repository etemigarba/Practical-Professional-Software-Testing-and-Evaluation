# Security-First Testing Playbook — Wiki

Companion documentation to the 56-slide course deck *Software Testing &
Evaluation: A Security-First Playbook* by **Prof. Etemi Joshua Garba** (Abuja,
Nigeria, 2026).

## Start here

| Page | What it covers |
|---|---|
| [Setup and Prerequisites](Setup-and-Prerequisites) | Install, run the suites, opt-in extras |
| [01 · Foundations](01-Foundations) | Quality models, risk banding, test strategy |
| [02 · Test Architecture](02-Test-Architecture) | Pyramid, unit, property, mutation, contract, flakiness |
| [03 · Security-First Testing](03-Security-First-Testing) | STRIDE, OWASP, authorisation, fuzzing, supply chain |
| [04 · Non-Functional and Production](04-Non-Functional-and-Production) | SLOs, chaos, accessibility, progressive delivery |
| [05 · Evaluation and Governance](05-Evaluation-and-Governance) | SSDF, triage, metrics, compliance, evidence |
| [06 · Adoption](06-Adoption) | Anti-patterns, checklist, staged roadmap |
| [Glossary](Glossary) | Every term and acronym used across the deck |

## The one-sentence version

Model the threats, turn each one into an executable test, gate the pipeline on
the result, and prove the provenance of everything you did not write yourself.

## What makes this repository unusual

It runs. Every technique the deck names has working code behind it, the twelve
places where the slides were wrong are corrected and documented, and the whole
suite executes offline in about a second.

It also gates against its own failure mode: an AST auditor runs over this
repository's own tests and CI fails if any of them asserts nothing.

## Licence

MIT, Copyright (c) 2026 Prof. Etemi Joshua Garba. **No permission is required**
to adopt, edit, refactor, translate, teach from, or commercially use this work.
