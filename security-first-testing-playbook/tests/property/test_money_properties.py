"""Slide 18 — property-based testing.

**Correction to slide 18.**  The slide derives both the total and the party
count from one generated list, so the two parameters are coupled by an artefact
of the strategy and the search space is far narrower than it looks.  Here they
are independent strategies, which is what makes the search meaningful.
"""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from stplaybook.money import Naira, split_bill

kobo_amounts = st.integers(min_value=0, max_value=10**12)
party_counts = st.integers(min_value=1, max_value=500)


@given(total_kobo=kobo_amounts, parties=party_counts)
def test_split_bill_never_loses_or_invents_a_kobo(total_kobo: int, parties: int) -> None:
    """Conservation: the shares sum to exactly the total."""
    shares = split_bill(Naira.from_kobo(total_kobo), parties=parties)

    assert sum(s.kobo for s in shares) == total_kobo


@given(total_kobo=kobo_amounts, parties=party_counts)
def test_split_bill_is_fair_to_within_one_kobo(total_kobo: int, parties: int) -> None:
    """Fairness, guaranteed by largest-remainder allocation."""
    shares = [s.kobo for s in split_bill(Naira.from_kobo(total_kobo), parties=parties)]

    assert max(shares) - min(shares) <= 1


@given(total_kobo=kobo_amounts, parties=party_counts)
def test_split_bill_produces_one_share_per_party(total_kobo: int, parties: int) -> None:
    shares = split_bill(Naira.from_kobo(total_kobo), parties=parties)

    assert len(shares) == parties
    assert all(s.kobo >= 0 for s in shares)


@given(a=kobo_amounts, b=kobo_amounts)
def test_addition_is_commutative(a: int, b: int) -> None:
    assert Naira.from_kobo(a) + Naira.from_kobo(b) == Naira.from_kobo(b) + Naira.from_kobo(a)


@given(a=kobo_amounts, b=kobo_amounts)
def test_subtracting_then_adding_restores_the_original(a: int, b: int) -> None:
    """Round-trip, on the branch where the subtraction is defined."""
    larger, smaller = max(a, b), min(a, b)

    restored = (Naira.from_kobo(larger) - Naira.from_kobo(smaller)) + Naira.from_kobo(smaller)

    assert restored == Naira.from_kobo(larger)


@given(kobo=kobo_amounts)
def test_kobo_round_trip_through_the_constructor_is_exact(kobo: int) -> None:
    """No float ever touches an amount, so this is exact at every magnitude."""
    amount = Naira.from_kobo(kobo)

    assert Naira(amount.naira).kobo == kobo


# Pinned counterexample (slide 18): the property found this once; the example
# keeps it fixed. A single party must receive the entire total, including the
# remainder that largest-remainder allocation would otherwise distribute.
def test_pinned_single_party_receives_the_entire_total() -> None:
    assert split_bill(Naira.from_kobo(9_999), parties=1) == [Naira.from_kobo(9_999)]
