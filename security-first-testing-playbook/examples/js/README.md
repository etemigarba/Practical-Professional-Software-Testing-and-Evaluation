# JavaScript examples (optional)

These three files preserve the deck's Pact, Playwright and k6 material in the
tools it actually names. They are **not required** to install, lint, type-check
or test the Python package — Node never enters the verification gate.

| File | Slide | Tool |
|---|---|---|
| `contract/consumer.pact.mjs` | 21 | Pact JS v3 (`PactV3`, `MatchersV3`) |
| `e2e/transfer.spec.mjs` | 22 | Playwright |
| `perf/transfer-slo.mjs` | 40 | k6 |

## Why they live here rather than in `tests/`

Deviation D4. The default suite must run with no Docker, no network and no
second language runtime. Moving these to `examples/` keeps that promise while
retaining the real APIs for readers who want them. The Python suite in
`tests/contract/` verifies the same interactions in-process.

## Corrections applied

Two of these files correct the slides they came from:

* **`consumer.pact.mjs`** — the slide uses `term({ matcher, generate })`, which
  is the Pact **v2** DSL; v3 uses `MatchersV3.regex(matcher, generate)`. The
  slide's builder chain also has no `.executeTest()`, so no pact file would ever
  be written.
* **`transfer-slo.mjs`** — the slide declares a `checks` threshold with no
  `check()` calls anywhere, so the gate measures nothing and passes vacuously.

## Running them

```bash
npm install                # only if you want to run these
npm run syntax-check       # what CI does: parse-only, no install needed
npm run test:e2e           # requires a running application
npm run test:perf          # requires k6 on PATH
```
