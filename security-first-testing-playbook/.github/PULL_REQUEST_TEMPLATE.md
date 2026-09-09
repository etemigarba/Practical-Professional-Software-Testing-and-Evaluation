## What this changes

<!-- One or two sentences. What behaviour is different after this merges? -->

## Why

<!-- The problem, not the solution. Link an issue if one exists. -->

## Per-pull-request checklist (slide 53)

- [ ] Unit, property, contract and security suites green
- [ ] Diff coverage ≥ 80% on changed lines
- [ ] `ruff check` and `ruff format --check` clean, zero warnings
- [ ] `mypy` clean under strict mode
- [ ] `make audit` reports no assertion-free tests
- [ ] Authorisation matrix updated if a role, endpoint or operation was added
- [ ] No new runtime dependency (or the case for one is made below)
- [ ] No Docker or network required by the default test run
- [ ] Fixtures are synthetic; no real personal, account or business data
- [ ] `docs/slide-to-code-map.md` updated if slide-described behaviour changed

## Risk band

<!-- critical / high / medium / low, and why. Critical and high changes need the
     deeper test depth set out in docs/testing.md. -->

## Anything a reviewer should look at first

<!-- Point at the part you are least sure about. -->
