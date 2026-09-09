# Contributing

## You do not need permission

This repository is MIT licensed with an explicit additional grant: **no explicit
permission is required to adopt, edit, refactor, translate, teach from, or
commercially use this work.** Fork it, rewrite it, teach from it, sell training
built on it. You need not ask, and you need not wait for a reply.

Contributions back are welcome but entirely optional. If you are adapting this
for your own course, forking is usually the better path — it keeps your changes
yours and spares you a review cycle.

## If you do want to contribute

### Before you open a pull request

Run the same gate CI runs:

```bash
make verify        # lint + typecheck + test + audit
```

All four must pass. In practice:

```bash
ruff check src tests && ruff format --check src tests
mypy
pytest
python -m stplaybook.quality.cli audit tests
```

### What a good pull request looks like here

This repository argues for particular practices, so it is held to them.

* **Every test asserts something specific.** `make audit` fails the build on any
  assertion-free test. Assertions on truthiness, or on whether a mock was
  called, are reported as weak.
* **Named exceptions, never bare `assert` for control flow** and never a generic
  `Exception`. Add a subclass to `src/stplaybook/errors.py` with structured
  attributes a test can assert on.
* **No runtime dependencies.** The package is standard library only, and that is
  a deliberate argument rather than an accident. Test-only and opt-in extras are
  fine; a new runtime import needs a case made in the pull request.
* **Nothing requires Docker or the network by default.** Anything that does goes
  behind an environment variable and a `pytest.mark`, and skips cleanly.
* **No real data.** Fixtures are synthetic. Under the Nigeria Data Protection
  Act 2023, a production extract in a test tree is a processing activity with
  consequences.
* **Corrections to the slides are documented.** If you change behaviour that a
  slide describes, record it in `docs/slide-to-code-map.md`.

### Commit and branch conventions

Conventional commit prefixes (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`,
`chore:`). One logical change per pull request.

### Reporting security issues

Not here — see `SECURITY.md`. Please do not open a public issue for anything you
believe is exploitable.

## Code of conduct

Participation is governed by `CODE_OF_CONDUCT.md`.
