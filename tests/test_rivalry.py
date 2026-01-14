"""Rivalry mechanic tests."""

from __future__ import annotations

from wrestlegm import constants
from wrestlegm.models import (
    Match,
    MatchTypeDefinition,
    MatchTypeModifiers,
    Promo,
    RivalryState,
    CooldownState,
    WrestlerDefinition,
)
from wrestlegm.state import GameState, normalize_pair


def build_match_type() -> MatchTypeDefinition:
    modifiers = MatchTypeModifiers(
        outcome_chaos=0.0,
        rating_bonus=0,
        rating_variance=0,
        stamina_cost_winner=0,
        stamina_cost_loser=0,
        popularity_delta_winner=0,
        popularity_delta_loser=0,
    )
    return MatchTypeDefinition(
        id="standard",
        name="Standard",
        description="",
        modifiers=modifiers,
    )


def build_roster() -> list[WrestlerDefinition]:
    return [
        WrestlerDefinition("a", "Alpha", "Face", 50, 50, 40),
        WrestlerDefinition("b", "Bravo", "Heel", 50, 50, 40),
        WrestlerDefinition("c", "Charlie", "Face", 50, 50, 40),
        WrestlerDefinition("d", "Delta", "Heel", 50, 50, 40),
        WrestlerDefinition("e", "Echo", "Face", 50, 50, 40),
        WrestlerDefinition("f", "Foxtrot", "Heel", 50, 50, 40),
        WrestlerDefinition("g", "Gamma", "Face", 50, 50, 40),
        WrestlerDefinition("h", "Hotel", "Heel", 50, 50, 40),
    ]


def seed_show(state: GameState) -> None:
    match_type_id = next(iter(state.match_types))
    slots = [
        Match(
            wrestler_ids=["a", "b"],
            match_category_id="singles",
            match_type_id=match_type_id,
        ),
        Promo(wrestler_id="c"),
        Match(
            wrestler_ids=["d", "e"],
            match_category_id="singles",
            match_type_id=match_type_id,
        ),
        Promo(wrestler_id="f"),
        Match(
            wrestler_ids=["g", "h"],
            match_category_id="singles",
            match_type_id=match_type_id,
        ),
    ]
    for index, slot in enumerate(slots):
        state.set_slot(index, slot)


def test_rivalry_progression_blowoff_and_cooldown() -> None:
    state = GameState(build_roster(), [build_match_type()], seed=10)

    for expected in range(1, constants.RIVALRY_LEVEL_CAP + 1):
        seed_show(state)
        state.run_show()
        assert state.rivalry_value_for_pair("a", "b") == expected
        assert state.cooldown_remaining_for_pair("a", "b") == 0

    seed_show(state)
    state.run_show()
    assert state.rivalry_value_for_pair("a", "b") == 0
    assert state.cooldown_remaining_for_pair("a", "b") == constants.COOLDOWN_SHOWS

    seed_show(state)
    state.run_show()
    assert state.rivalry_value_for_pair("a", "b") == 0
    assert state.cooldown_remaining_for_pair("a", "b") == constants.COOLDOWN_SHOWS - 1


def test_rivalry_emojis_for_match_ordering() -> None:
    state = GameState(build_roster(), [build_match_type()], seed=11)

    key_ab = normalize_pair("a", "b")
    key_ac = normalize_pair("a", "c")
    key_bc = normalize_pair("b", "c")

    state.rivalry_states[key_ab] = RivalryState("a", "b", rivalry_value=1)
    state.cooldown_states[key_ac] = CooldownState("a", "c", remaining_shows=6)
    state.rivalry_states[key_bc] = RivalryState("b", "c", rivalry_value=4)

    emojis = state.rivalry_emojis_for_match(["a", "b", "c"])
    assert emojis == "⚡🧊💥"
