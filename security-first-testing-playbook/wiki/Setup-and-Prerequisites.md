# Setup and Prerequisites

## What you need

| | Required | Version |
|---|---|---|
| Python | Yes | 3.12 or later |
| pip | Yes | any recent |
| Docker | No | only for the opt-in Postgres test |
| Node.js | No | only for the optional JS examples |
| Network | No | only for the initial install |

Tested on Linux, macOS and Windows against Python 3.12 and 3.13.

## Install

```bash
git clone https://github.com/etemigarba/security-first-testing-playbook
cd security-first-testing-playbook
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

Expected: **139 passed, 1 skipped** in about a second. The skip is the Postgres
integration test, which is opt-in by design.

## Optional extras

```bash
pip install -e ".[postgres]"   # real-engine integration test (needs Docker)
pip install -e ".[fuzz]"       # coverage-guided fuzzing via Atheris
pip install -e ".[mutation]"   # mutation testing via mutmut
pip install -e ".[sbom]"       # CycloneDX SBOM generation
```

Each suite skips cleanly when its extra is absent, so a fresh clone never fails
for a reason you did not choose.

## Environment variables

Copy `.env.example` to `.env`. Everything defaults to off.

| Variable | Default | Effect |
|---|---|---|
| `STP_USE_POSTGRES` | `0` | Run the integration test against real Postgres |
| `STP_POSTGRES_IMAGE` | `postgres:17-alpine` | Pinned image; `:latest` is refused |
| `STP_ENABLE_FUZZ` | `0` | Enable live fuzzing |
| `STP_FUZZ_SECONDS` | `30` | Fuzzing budget |
| `STP_DIFF_COVERAGE_FLOOR` | `80` | Diff-coverage gate, percent |
| `STP_MUTATION_SCORE_FLOOR` | `70` | Mutation-score gate, percent |

Values are validated at boot by `src/stplaybook/config.py`. A malformed one
raises `ConfigurationError` immediately rather than halfway through a suite.

## Make targets

```bash
make verify      # lint + typecheck + test + audit — what CI runs
make test        # pytest
make coverage    # with branch coverage
make audit       # fail on any assertion-free test
make lint        # ruff check + format check
make typecheck   # mypy strict
make mutation    # nightly, opt-in
make fuzz        # opt-in
make sbom        # generate a CycloneDX SBOM
```

## Troubleshooting

**`ModuleNotFoundError: stplaybook`** — install in editable mode:
`pip install -e ".[dev]"`. The package uses a `src/` layout, so it is not
importable from the working directory alone.

**Postgres test fails rather than skipping** — you have set
`STP_USE_POSTGRES=1` without a container runtime. Unset it, or start Docker.

**`atheris` will not install** — wheels are not published for every platform and
Python version. Fuzzing is opt-in for exactly this reason; the corpus replay
tests in `tests/fuzz/test_corpus_replay.py` run without it.

**Windows path or encoding errors** — all files are UTF-8 with LF endings, and
`.editorconfig` enforces both. Ensure Git is not converting line endings:
`git config core.autocrlf false`.
