"""Replay the fuzzing corpus as ordinary tests.

Slide 34: seed the corpus, then keep it.  Every input here — valid seeds and
crash reproducers alike — runs in the default offline suite, so a regression is
caught on the pull request rather than on the next nightly fuzz run.
"""

from __future__ import annotations

import random
from pathlib import Path

import pytest

from stplaybook.errors import InvalidStatement
from stplaybook.parsing import Statement, parse_bank_statement
from tests.factories import make_statement_bytes

CORPUS = Path(__file__).parent / "corpus"


def _parse_or_reason(data: bytes) -> Statement | str:
    """Apply the parser contract, returning either the statement or the reason."""
    try:
        return parse_bank_statement(data)
    except InvalidStatement as err:
        return err.reason


def _corpus_files() -> list[Path]:
    return sorted(CORPUS.glob("*.txt"))


def test_the_corpus_is_committed_to_the_repository() -> None:
    """A corpus that lives only on a fuzzing box is a corpus you will lose."""
    assert len(_corpus_files()) >= 4


@pytest.mark.parametrize("path", _corpus_files(), ids=lambda p: p.stem)
def test_every_corpus_input_satisfies_the_parser_contract(path: Path) -> None:
    data = path.read_bytes()

    outcome = _parse_or_reason(data)

    if isinstance(outcome, str):
        assert outcome != ""
        return

    assert outcome.total.kobo == sum(line.amount.kobo for line in outcome.lines)


def test_a_generated_seed_parses_and_balances() -> None:
    data = make_statement_bytes(random.Random(7), lines=5)

    statement = parse_bank_statement(data)

    assert len(statement.lines) == 5
    assert statement.total.kobo == sum(line.amount.kobo for line in statement.lines)


def test_oversized_input_is_bounded_rather_than_hanging() -> None:
    """The 'never hangs' half of the contract, enforced structurally."""
    with pytest.raises(InvalidStatement) as err:
        parse_bank_statement(b"H|NGN|1043321818\n" + b"L|x|1\n" * 200_000)
    assert "exceeds" in err.value.reason
