"""Simulation tests for WrestleGM MVP."""

from __future__ import annotations

import random

from wrestlegm import constants
from wrestlegm.models import Match, MatchResult, MatchTypeDefinition, MatchTypeModifiers, Show, StatDelta, WrestlerDefinition, WrestlerState
from wrestlegm.sim import aggregate_show_rating, simulate_outcome, simulate_rating, simulate_show, simulate_stat_deltas
from wrestlegm.state import GameState


def build_roster() -> list[WrestlerDefinition]:
    return [
        WrestlerDefinition(id="a", name="Alpha", alignment="Face", popularity=90, stamina=90),
        WrestlerDefinition(id="b", name="Bravo", alignment="Heel", popularity=10, stamina=10),
        WrestlerDefinition(id="c", name="Charlie", alignment="Face", popularity=50, stamina=50),
    ]


def build_match_types() -> list[MatchTypeDefinition]:
    modifiers = MatchTypeModifiers(
        outcome_chaos=0.2,
        rating_bonus=5,
        rating_variance=3,
        stamina_cost_winner=10,
        stamina_cost_loser=12,
        popularity_delta_winner=2,
        popularity_delta_loser=-1,
    )
    return [
        MatchTypeDefinition(id="singles", name="Singles", description="", modifiers=modifiers)
    ]


def test_deterministic_simulation() -> None:
    roster_defs = build_roster()
    match_types = build_match_types()
    roster_state = {
        w.id: WrestlerState(
            id=w.id,
            name=w.name,
            alignment=w.alignment,
            popularity=w.popularity,
            stamina=w.stamina,
        )
        for w in roster_defs
    }
    match_type_map = {m.id: m for m in match_types}
    matches = [Match(wrestler_a_id="a", wrestler_b_id="b", match_type_id="singles")]

    rng_one = random.Random(123)
    rng_two = random.Random(123)

    results_one = simulate_show(matches, roster_state, match_type_map, rng_one)
    results_two = simulate_show(matches, roster_state, match_type_map, rng_two)

    assert [(r.winner_id, r.loser_id, r.rating) for r in results_one] == [
        (r.winner_id, r.loser_id, r.rating) for r in results_two
    ]


def test_outcome_probability_clamps() -> None:
    wrestler_a = WrestlerState("a", "Alpha", "Face", popularity=100, stamina=100)
    wrestler_b = WrestlerState("b", "Bravo", "Heel", popularity=0, stamina=0)
    modifiers = MatchTypeModifiers(
        outcome_chaos=0.0,
        rating_bonus=0,
        rating_variance=0,
        stamina_cost_winner=0,
        stamina_cost_loser=0,
        popularity_delta_winner=0,
        popularity_delta_loser=0,
    )
    _, _, debug = simulate_outcome(wrestler_a, wrestler_b, modifiers, random.Random(1))
    assert constants.P_MIN <= debug.p_base <= constants.P_MAX


def test_rating_bounds() -> None:
    wrestler_a = WrestlerState("a", "Alpha", "Face", popularity=100, stamina=100)
    wrestler_b = WrestlerState("b", "Bravo", "Heel", popularity=0, stamina=0)
    modifiers = MatchTypeModifiers(
        outcome_chaos=0.0,
        rating_bonus=0,
        rating_variance=50,
        stamina_cost_winner=0,
        stamina_cost_loser=0,
        popularity_delta_winner=0,
        popularity_delta_loser=0,
    )
    match_type = MatchTypeDefinition("test", "Test", "", modifiers)
    rating, debug = simulate_rating(wrestler_a, wrestler_b, match_type, random.Random(2))
    assert 0.0 <= rating <= 5.0
    assert 0 <= debug.rating_100 <= 100


def test_delta_correctness() -> None:
    modifiers = MatchTypeModifiers(
        outcome_chaos=0.0,
        rating_bonus=0,
        rating_variance=0,
        stamina_cost_winner=7,
        stamina_cost_loser=9,
        popularity_delta_winner=3,
        popularity_delta_loser=-2,
    )
    deltas = simulate_stat_deltas("a", "b", modifiers)
    assert deltas["a"] == StatDelta(popularity=3, stamina=-7)
    assert deltas["b"] == StatDelta(popularity=-2, stamina=-9)


def test_show_rating_aggregation() -> None:
    results = [
        MatchResult(
            winner_id="a",
            loser_id="b",
            rating=4.0,
            match_type_id="singles",
            applied_modifiers=build_match_types()[0].modifiers,
            stat_deltas={},
        ),
        MatchResult(
            winner_id="b",
            loser_id="a",
            rating=2.0,
            match_type_id="singles",
            applied_modifiers=build_match_types()[0].modifiers,
            stat_deltas={},
        ),
    ]
    assert aggregate_show_rating(results) == 3.0


def test_clamp_and_recovery() -> None:
    roster = [
        WrestlerDefinition(id="a", name="Alpha", alignment="Face", popularity=99, stamina=5),
        WrestlerDefinition(id="b", name="Bravo", alignment="Heel", popularity=1, stamina=95),
        WrestlerDefinition(id="c", name="Charlie", alignment="Face", popularity=50, stamina=90),
    ]
    match_types = build_match_types()
    state = GameState(roster, match_types, seed=42)

    result = MatchResult(
        winner_id="a",
        loser_id="b",
        rating=3.0,
        match_type_id="singles",
        applied_modifiers=match_types[0].modifiers,
        stat_deltas={
            "a": StatDelta(popularity=10, stamina=10),
            "b": StatDelta(popularity=-20, stamina=-200),
        },
    )
    state.apply_show_results(
        show=Show(
            show_index=1,
            scheduled_matches=[],
            results=[result],
            show_rating=3.0,
        )
    )

    assert state.roster["a"].popularity == 100
    assert state.roster["a"].stamina == 15
    assert state.roster["b"].popularity == 0
    assert state.roster["b"].stamina == 0
    assert state.roster["c"].stamina == 100
