"""GameState validation tests for multi-man matches."""

from __future__ import annotations

from wrestlegm import constants
from wrestlegm.models import Match, MatchTypeDefinition, MatchTypeModifiers, WrestlerDefinition
from wrestlegm.state import GameState


def build_match_type(min_wrestlers: int, max_wrestlers: int) -> MatchTypeDefinition:
    modifiers = MatchTypeModifiers(
        outcome_chaos=0.2,
        rating_bonus=0,
        rating_variance=0,
        stamina_cost_winner=5,
        stamina_cost_loser=6,
        popularity_delta_winner=1,
        popularity_delta_loser=-1,
    )
    return MatchTypeDefinition(
        id="multi",
        name="Multi",
        description="",
        modifiers=modifiers,
        min_wrestlers=min_wrestlers,
        max_wrestlers=max_wrestlers,
    )


def build_roster() -> list[WrestlerDefinition]:
    return [
        WrestlerDefinition("a", "Alpha", "Face", 50, 50, 40),
        WrestlerDefinition("b", "Bravo", "Heel", 50, 50, 40),
        WrestlerDefinition("c", "Charlie", "Face", 50, 50, 40),
    ]


def test_validate_match_size_mismatch() -> None:
    state = GameState(build_roster(), [build_match_type(3, 3)])
    match = Match(wrestler_ids=["a", "b"], match_type_id="multi")
    assert "invalid_wrestler_count" in state.validate_match(match, slot_index=0)


def test_validate_match_duplicate_wrestlers() -> None:
    state = GameState(build_roster(), [build_match_type(2, 2)])
    match = Match(wrestler_ids=["a", "a"], match_type_id="multi")
    assert "duplicate_wrestler" in state.validate_match(match, slot_index=0)


def test_validate_match_low_stamina_blocked() -> None:
    roster = build_roster()
    roster[0] = WrestlerDefinition(
        "a",
        "Alpha",
        "Face",
        popularity=50,
        stamina=constants.STAMINA_MIN_BOOKABLE,
        mic_skill=40,
    )
    state = GameState(roster, [build_match_type(2, 2)])
    match = Match(wrestler_ids=["a", "b"], match_type_id="multi")
    assert "not_enough_stamina" in state.validate_match(match, slot_index=0)
