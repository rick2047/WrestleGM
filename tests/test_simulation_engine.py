"""Simulation engine tests for WrestleGM MVP."""

from __future__ import annotations

from wrestlegm import constants
from wrestlegm.models import (
    Match,
    MatchResult,
    MatchTypeDefinition,
    MatchTypeModifiers,
    Promo,
    PromoResult,
    Show,
    StatDelta,
    WrestlerDefinition,
    WrestlerState,
)
from wrestlegm.sim import SimulationEngine
from wrestlegm.state import ShowApplier


def build_roster() -> list[WrestlerDefinition]:
    return [
        WrestlerDefinition(
            id="a",
            name="Alpha",
            alignment="Face",
            popularity=90,
            stamina=90,
            mic_skill=80,
        ),
        WrestlerDefinition(
            id="b",
            name="Bravo",
            alignment="Heel",
            popularity=10,
            stamina=10,
            mic_skill=40,
        ),
        WrestlerDefinition(
            id="c",
            name="Charlie",
            alignment="Face",
            popularity=50,
            stamina=50,
            mic_skill=60,
        ),
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
        MatchTypeDefinition(
            id="singles",
            name="Singles",
            description="",
            modifiers=modifiers,
        )
    ]


def build_roster_state() -> dict[str, WrestlerState]:
    return {
        w.id: WrestlerState(
            id=w.id,
            name=w.name,
            alignment=w.alignment,
            popularity=w.popularity,
            stamina=w.stamina,
            mic_skill=w.mic_skill,
        )
        for w in build_roster()
    }


class TestDeterminism:
    def test_same_seed_same_show_results(self) -> None:
        roster_state = build_roster_state()
        match_types = build_match_types()
        match_type_map = {m.id: m for m in match_types}
        matches = [Match(wrestler_ids=["a", "b"], match_category_id="singles", match_type_id="singles")]

        engine_one = SimulationEngine(seed=123)
        engine_two = SimulationEngine(seed=123)

        results_one = engine_one.simulate_show(matches, roster_state, match_type_map)
        results_two = engine_two.simulate_show(matches, roster_state, match_type_map)

        assert [(r.winner_id, r.non_winner_ids, r.rating) for r in results_one] == [
            (r.winner_id, r.non_winner_ids, r.rating) for r in results_two
        ]

    def test_same_seed_same_match_results(self) -> None:
        roster_state = build_roster_state()
        match_types = build_match_types()
        match_type_map = {m.id: m for m in match_types}
        match = Match(wrestler_ids=["a", "b"], match_category_id="singles", match_type_id="singles")

        engine_one = SimulationEngine(seed=321)
        engine_two = SimulationEngine(seed=321)

        result_one = engine_one.simulate_match(match, roster_state, match_type_map)
        result_two = engine_two.simulate_match(match, roster_state, match_type_map)

        assert (result_one.winner_id, result_one.non_winner_ids, result_one.rating) == (
            result_two.winner_id,
            result_two.non_winner_ids,
            result_two.rating,
        )

    def test_same_seed_same_multi_man_results(self) -> None:
        roster_state = build_roster_state()
        modifiers = build_match_types()[0].modifiers
        match_type = MatchTypeDefinition(
            id="triple",
            name="Triple Threat",
            description="",
            modifiers=modifiers,
        )
        match_type_map = {match_type.id: match_type}
        match = Match(wrestler_ids=["a", "b", "c"], match_category_id="triple-threat", match_type_id="triple")

        engine_one = SimulationEngine(seed=555)
        engine_two = SimulationEngine(seed=555)

        result_one = engine_one.simulate_match(match, roster_state, match_type_map)
        result_two = engine_two.simulate_match(match, roster_state, match_type_map)

        assert (result_one.winner_id, result_one.non_winner_ids, result_one.rating) == (
            result_two.winner_id,
            result_two.non_winner_ids,
            result_two.rating,
        )


class TestMatchSimulation:
    def test_outcome_probability_clamps(self) -> None:
        wrestler_a = WrestlerState("a", "Alpha", "Face", popularity=100, stamina=100, mic_skill=50)
        wrestler_b = WrestlerState("b", "Bravo", "Heel", popularity=0, stamina=0, mic_skill=50)
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
        _, _, debug = engine.simulate_outcome([wrestler_a, wrestler_b], modifiers)
        assert abs(sum(debug.p_base) - 1) < 1e-6
        assert all(0 <= value <= 1 for value in debug.p_base)


    def test_rating_bounds(self) -> None:
        wrestler_a = WrestlerState("a", "Alpha", "Face", popularity=100, stamina=100, mic_skill=50)
        wrestler_b = WrestlerState("b", "Bravo", "Heel", popularity=0, stamina=0, mic_skill=50)
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
        rating, debug = engine.simulate_rating([wrestler_a, wrestler_b], match_type)
        assert 0.0 <= rating <= 5.0
        assert 0 <= debug.rating_100 <= 100

    def test_alignment_modifiers(self) -> None:
        face = WrestlerState("a", "Alpha", "Face", popularity=50, stamina=50, mic_skill=50)
        heel = WrestlerState("b", "Bravo", "Heel", popularity=50, stamina=50, mic_skill=50)
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
        _, debug = engine.simulate_rating([face, heel], match_type)
        assert debug.alignment_mod == constants.ALIGN_BONUS

    def test_alignment_modifiers_multi_man(self) -> None:
        face = WrestlerState("a", "Alpha", "Face", popularity=50, stamina=50, mic_skill=50)
        heel = WrestlerState("b", "Bravo", "Heel", popularity=50, stamina=50, mic_skill=50)
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
        engine = SimulationEngine(seed=9)
        _, debug_all_faces = engine.simulate_rating([face, face], match_type)
        assert debug_all_faces.alignment_mod == 0
        _, debug_all_heels = engine.simulate_rating([heel, heel, heel], match_type)
        assert debug_all_heels.alignment_mod == -2 * constants.ALIGN_BONUS
        _, debug_heels_majority = engine.simulate_rating([heel, heel, face], match_type)
        assert debug_heels_majority.alignment_mod == constants.ALIGN_BONUS
        _, debug_faces_majority = engine.simulate_rating([face, face, heel], match_type)
        assert debug_faces_majority.alignment_mod == -2 * constants.ALIGN_BONUS


class TestMatchSimulationStatDeltas:
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
        deltas = engine.simulate_stat_deltas("a", ["b", "c"], modifiers)
        assert deltas["a"] == StatDelta(popularity=3, stamina=-7)
        assert deltas["b"] == StatDelta(popularity=-2, stamina=-9)
        assert deltas["c"] == StatDelta(popularity=-2, stamina=-9)


class TestPromoSimulation:
    def test_promo_determinism(self) -> None:
        roster_state = build_roster_state()
        engine_one = SimulationEngine(seed=101)
        engine_two = SimulationEngine(seed=101)

        promo = Promo(wrestler_id="a")
        result_one = engine_one.simulate_promo(promo, roster_state)
        result_two = engine_two.simulate_promo(promo, roster_state)

        assert result_one.rating == result_two.rating
        assert result_one.stat_deltas == result_two.stat_deltas

    def test_promo_delta_threshold(self) -> None:
        engine = SimulationEngine(seed=202)
        low = engine.simulate_promo_deltas(49)
        high = engine.simulate_promo_deltas(50)
        assert low == StatDelta(popularity=-5, stamina=constants.STAMINA_RECOVERY_PER_SHOW // 2)
        assert high == StatDelta(popularity=5, stamina=constants.STAMINA_RECOVERY_PER_SHOW // 2)


class TestShowSimulation:
    def test_show_rating_aggregation(self) -> None:
        results = [
            MatchResult(
                winner_id="a",
                non_winner_ids=["b"],
                rating=4.0,
                match_category_id="singles",
                match_type_id="singles",
                applied_modifiers=build_match_types()[0].modifiers,
                stat_deltas={},
            ),
            PromoResult(
                wrestler_id="a",
                rating=1.0,
                stat_deltas={},
            ),
            MatchResult(
                winner_id="b",
                non_winner_ids=["a"],
                rating=2.0,
                match_category_id="singles",
                match_type_id="singles",
                applied_modifiers=build_match_types()[0].modifiers,
                stat_deltas={},
            ),
        ]
        engine = SimulationEngine(seed=5)
        assert engine.aggregate_show_rating(results) == 7.0 / 3.0

    def test_empty_show_rating(self) -> None:
        engine = SimulationEngine(seed=6)
        assert engine.aggregate_show_rating([]) == 0.0


class TestMutation:
    def test_clamp_and_recovery(self) -> None:
        roster = [
            WrestlerDefinition(
                id="a",
                name="Alpha",
                alignment="Face",
                popularity=99,
                stamina=5,
                mic_skill=50,
            ),
            WrestlerDefinition(
                id="b",
                name="Bravo",
                alignment="Heel",
                popularity=1,
                stamina=95,
                mic_skill=50,
            ),
            WrestlerDefinition(
                id="c",
                name="Charlie",
                alignment="Face",
                popularity=50,
                stamina=90,
                mic_skill=50,
            ),
        ]
        roster_state = {
            w.id: WrestlerState(
                id=w.id,
                name=w.name,
                alignment=w.alignment,
                popularity=w.popularity,
                stamina=w.stamina,
                mic_skill=w.mic_skill,
            )
            for w in roster
        }
        match_types = build_match_types()

        result = MatchResult(
            winner_id="a",
            non_winner_ids=["b"],
            rating=3.0,
            match_category_id="singles",
            match_type_id="singles",
            applied_modifiers=match_types[0].modifiers,
            stat_deltas={
                "a": StatDelta(popularity=10, stamina=10),
                "b": StatDelta(popularity=-20, stamina=-200),
            },
        )
        show = Show(
            show_index=1,
            scheduled_slots=[],
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
