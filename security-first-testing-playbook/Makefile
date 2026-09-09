# Verification gates for the security-first testing playbook.
# Every target here is also a job in .github/workflows/ci.yml.

.PHONY: help install lint format typecheck test coverage audit mutation fuzz sbom verify clean

help:
	@grep -E '^[a-z-]+:.*?##' $(MAKEFILE_LIST) | sed 's/:.*##/\t/' | column -t -s "$$(printf '\t')"

install:  ## Install the package and dev toolchain
	python -m pip install -e ".[dev]"

lint:  ## Lint and format check, zero warnings tolerated
	ruff check src tests
	ruff format --check src tests

format:  ## Apply formatting
	ruff format src tests
	ruff check --fix src tests

typecheck:  ## Strict type check
	mypy

test:  ## Full suite; no Docker, no network
	pytest

coverage:  ## Suite with branch coverage
	pytest --cov --cov-report=term-missing --cov-report=xml

audit:  ## Fail if any test in this repository asserts nothing
	python -m stplaybook.quality.cli audit tests

mutation:  ## Nightly, not a PR gate (slide 19)
	mutmut run --paths-to-mutate src/stplaybook

fuzz:  ## Opt-in coverage-guided fuzzing (slide 34)
	STP_ENABLE_FUZZ=1 python tests/fuzz/fuzz_statement_parser.py -atheris_runs=200000

sbom:  ## Generate a CycloneDX SBOM at build time (slide 35)
	cyclonedx-py environment -o sbom.cdx.json

verify: lint typecheck test audit  ## Everything the PR gate runs

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage coverage.xml dist build
	find . -name __pycache__ -type d -exec rm -rf {} +
