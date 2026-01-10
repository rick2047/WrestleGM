"""Simulation engine tests for WrestleGM MVP."""

from __future__ import annotations

from wrestlegm import constants
from wrestlegm.models import (
    Match,
    MatchResult,
    MatchTypeDefinition,
    MatchTypeModifiers,
    Show,
    StatDelta,
    WrestlerDefinition,
    WrestlerState,
)
from wrestlegm.sim import SimulationEngine
from wrestlegm.state import ShowApplier


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
    return [MatchTypeDefinition(id="singles", name="Singles", description="", modifiers=modifiers)]


def build_roster_state() -> dict[str, WrestlerState]:
    return {
        w.id: WrestlerState(
            id=w.id,
            name=w.name,
            alignment=w.alignment,
            popularity=w.popularity,
            stamina=w.stamina,
        )
        for w in build_roster()
    }


class TestSimulationEngineDeterminism:
    def test_same_seed_same_show_results(self) -> None:
        roster_state = build_roster_state()
        match_types = build_match_types()
        match_type_map = {m.id: m for m in match_types}
        matches = [Match(wrestler_a_id="a", wrestler_b_id="b", match_type_id="singles")]

        engine_one = SimulationEngine(seed=123)
        engine_two = SimulationEngine(seed=123)

        results_one = engine_one.simulate_show(matches, roster_state, match_type_map)
        results_two = engine_two.simulate_show(matches, roster_state, match_type_map)

        assert [(r.winner_id, r.loser_id, r.rating) for r in results_one] == [
            (r.winner_id, r.loser_id, r.rating) for r in results_two
        ]

    def test_same_seed_same_match_results(self) -> None:
        roster_state = build_roster_state()
        match_types = build_match_types()
        match_type_map = {m.id: m for m in match_types}
        match = Match(wrestler_a_id="a", wrestler_b_id="b", match_type_id="singles")

        engine_one = SimulationEngine(seed=321)
        engine_two = SimulationEngine(seed=321)

        result_one = engine_one.simulate_match(match, roster_state, match_type_map)
        result_two = engine_two.simulate_match(match, roster_state, match_type_map)

        assert (result_one.winner_id, result_one.loser_id, result_one.rating) == (
            result_two.winner_id,
            result_two.loser_id,
            result_two.rating,
        )


class TestOutcomeSimulation:
    def test_outcome_probability_clamps(self) -> None:
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
        engine = SimulationEngine(seed=1)
        _, _, debug = engine.simulate_outcome(wrestler_a, wrestler_b, modifiers)
        assert constants.P_MIN <= debug.p_base <= constants.P_MAX


class TestRatingSimulation:
    def test_rating_bounds(self) -> None:
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
        engine = SimulationEngine(seed=2)
        rating, debug = engine.simulate_rating(wrestler_a, wrestler_b, match_type)
        assert 0.0 <= rating <= 5.0
        assert 0 <= debug.rating_100 <= 100

    def test_alignment_modifiers(self) -> None:
        face = WrestlerState("a", "Alpha", "Face", popularity=50, stamina=50)
        heel = WrestlerState("b", "Bravo", "Heel", popularity=50, stamina=50)
        modifiers = MatchTypeModifiers(
            outcome_chaos=0.0,
            rating_bonus=0,
            rating_variance=0,
            stamina_cost_winner=0,
            stamina_cost_loser=0,
            popularity_delta_winner=0,
            popularity_delta_loser=0,
        )
        match_type = MatchTypeDefinition("test", "Test", "", modifiers)
        engine = SimulationEngine(seed=3)
        _, debug = engine.simulate_rating(face, heel, match_type)
        assert debug.alignment_mod == constants.ALIGN_BONUS


class TestStatDeltas:
    def test_delta_correctness(self) -> None:
        modifiers = MatchTypeModifiers(
            outcome_chaos=0.0,
            rating_bonus=0,
            rating_variance=0,
            stamina_cost_winner=7,
            stamina_cost_loser=9,
            popularity_delta_winner=3,
            popularity_delta_loser=-2,
        )
        engine = SimulationEngine(seed=4)
        deltas = engine.simulate_stat_deltas("a", "b", modifiers)
        assert deltas["a"] == StatDelta(popularity=3, stamina=-7)
        assert deltas["b"] == StatDelta(popularity=-2, stamina=-9)


class TestShowSimulation:
    def test_show_rating_aggregation(self) -> None:
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
        engine = SimulationEngine(seed=5)
        assert engine.aggregate_show_rating(results) == 3.0

    def test_empty_show_rating(self) -> None:
        engine = SimulationEngine(seed=6)
        assert engine.aggregate_show_rating([]) == 0.0


class TestShowApplier:
    def test_clamp_and_recovery(self) -> None:
        roster = [
            WrestlerDefinition(id="a", name="Alpha", alignment="Face", popularity=99, stamina=5),
            WrestlerDefinition(id="b", name="Bravo", alignment="Heel", popularity=1, stamina=95),
            WrestlerDefinition(id="c", name="Charlie", alignment="Face", popularity=50, stamina=90),
        ]
        roster_state = {
            w.id: WrestlerState(
                id=w.id,
                name=w.name,
                alignment=w.alignment,
                popularity=w.popularity,
                stamina=w.stamina,
            )
            for w in roster
        }
        match_types = build_match_types()

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
        show = Show(
            show_index=1,
            scheduled_matches=[],
            results=[result],
            show_rating=3.0,
        )

        applier = ShowApplier()
        applier.apply(show, roster_state)

        assert roster_state["a"].popularity == 100
        assert roster_state["a"].stamina == 15
        assert roster_state["b"].popularity == 0
        assert roster_state["b"].stamina == 0
        assert roster_state["c"].stamina == 100
