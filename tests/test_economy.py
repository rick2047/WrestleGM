"""Economy calculation tests."""

from __future__ import annotations

import random

from wrestlegm import constants, economy
from wrestlegm.models import (
    CooldownState,
    Match,
    match_category_by_id,
    MatchTypeDefinition,
    MatchTypeModifiers,
    Promo,
    RivalryState,
    WrestlerDefinition,
    WrestlerState,
)
from wrestlegm.rivalries import RivalryManager
from wrestlegm.state import GameState


def build_match_type(base_cost: int = 100) -> MatchTypeDefinition:
    modifiers = MatchTypeModifiers(
        outcome_chaos=0.2,
        rating_bonus=0,
        rating_variance=6,
        stamina_cost_winner=12,
        stamina_cost_loser=14,
        popularity_delta_winner=2,
        popularity_delta_loser=-1,
    )
    return MatchTypeDefinition(
        id="standard",
        name="Standard",
        description="",
        modifiers=modifiers,
        base_cost=base_cost,
    )


def build_roster() -> dict[str, WrestlerState]:
    return {
        "a": WrestlerState("a", "A", "Face", 50, 20, 50),
        "b": WrestlerState("b", "B", "Heel", 60, 20, 50),
        "c": WrestlerState("c", "C", "Face", 30, 5, 50),
    }


def build_definitions() -> tuple[list[WrestlerDefinition], list[MatchTypeDefinition]]:
    wrestlers = [
        WrestlerDefinition("a", "A", "Face", 50, 20, 50),
        WrestlerDefinition("b", "B", "Heel", 60, 20, 50),
        WrestlerDefinition("c", "C", "Face", 55, 20, 50),
        WrestlerDefinition("d", "D", "Heel", 52, 20, 50),
        WrestlerDefinition("e", "E", "Face", 48, 20, 50),
        WrestlerDefinition("f", "F", "Heel", 47, 20, 50),
        WrestlerDefinition("g", "G", "Face", 46, 20, 50),
        WrestlerDefinition("h", "H", "Heel", 45, 20, 50),
    ]
    return wrestlers, [build_match_type(base_cost=100)]


def build_state_slots(state: GameState) -> list[Match | Promo]:
    singles = match_category_by_id(1)
    if singles is None:
        raise AssertionError("Missing singles match category.")
    return [
        Match([state.roster["a"], state.roster["b"]], singles, "standard"),
        Promo(state.roster["c"]),
        Match([state.roster["d"], state.roster["e"]], singles, "standard"),
        Promo(state.roster["f"]),
        Match([state.roster["g"], state.roster["h"]], singles, "standard"),
    ]


def test_show_cost_unique_wrestler_billing() -> None:
    simulator = economy.EconomySimulator()
    roster = build_roster()
    match_types = {"standard": build_match_type(base_cost=200)}
    singles = match_category_by_id(1)
    if singles is None:
        raise AssertionError("Missing singles match category.")
    slots = [
        Match([roster["a"], roster["b"]], singles, "standard"),
        Promo(roster["a"]),
    ]
    cost = simulator.show_cost(slots, match_types)
    expected = (
        roster["a"].booking_price()
        + roster["b"].booking_price()
        + 200
    )
    assert cost == expected


def test_economy_inputs_alignment_and_pop_sum() -> None:
    simulator = economy.EconomySimulator()
    roster = build_roster()
    rivalry = RivalryManager()
    singles = match_category_by_id(1)
    if singles is None:
        raise AssertionError("Missing singles match category.")
    slots = [
        Match([roster["a"], roster["b"]], singles, "standard"),
        Promo(roster["c"]),
    ]
    inputs = simulator.audience_inputs_for_slots(slots, rivalry)
    assert inputs.pop_sum == roster["a"].popularity + roster["b"].popularity + roster["c"].popularity
    assert inputs.align_score == 1


def test_economy_inputs_rivalry_and_cooldown_counts() -> None:
    simulator = economy.EconomySimulator()
    roster = build_roster()
    rivalry = RivalryManager()
    rivalry.rivalry_states[("a", "b")] = RivalryState("a", "b", rivalry_value=1)
    rivalry.rivalry_states[("b", "c")] = RivalryState("b", "c", rivalry_value=2)
    rivalry.cooldown_states[("a", "c")] = CooldownState("a", "c", remaining_shows=4)
    triple = match_category_by_id(2)
    if triple is None:
        raise AssertionError("Missing triple-threat match category.")
    slots = [Match([roster["a"], roster["b"], roster["c"]], triple, "standard")]

    inputs = simulator.audience_inputs_for_slots(slots, rivalry)

    assert inputs.rivalry_count == 2
    assert inputs.cooldown_count == 1


def test_compute_audience_base_and_curve() -> None:
    inputs = economy.EconomyInputs(pop_sum=100, align_score=1, rivalry_count=0, cooldown_count=0)
    audience = economy.EconomySimulator._compute_audience(inputs, 1.0)
    expected = (
        100 * constants.AUDIENCE_POP_MULTIPLIER
        + constants.AUDIENCE_ALIGN_BONUS
    )
    assert audience == expected


def test_merch_rate_is_clamped() -> None:
    rate = economy.EconomySimulator._merch_rate(5.0)
    assert rate <= constants.MERCH_RATE_MAX
    assert rate >= constants.MERCH_RATE_MIN


class FixedRNG:
    def __init__(self, values: list[float]) -> None:
        self._values = values
        self._index = 0

    def uniform(self, _min: float, _max: float) -> float:
        value = self._values[self._index]
        self._index += 1
        return value


def test_rng_swing_bounds_applied() -> None:
    simulator = economy.EconomySimulator()
    roster = build_roster()
    match_types = {"standard": build_match_type(base_cost=0)}
    slots = [Match([roster["a"], roster["b"]], "singles", "standard"), Promo(roster["c"])]
    rivalry = RivalryManager()
    rng = FixedRNG([constants.ECONOMY_RNG_MIN, constants.ECONOMY_RNG_MAX])
    result = simulator.compute_show(slots, match_types, rivalry, rng, 3.0)
    assert result.audience >= 0
    assert result.gate_income == result.audience * constants.GATE_RATE


def test_economy_determinism_with_seed() -> None:
    simulator = economy.EconomySimulator()
    roster = build_roster()
    match_types = {"standard": build_match_type(base_cost=100)}
    slots = [Match([roster["a"], roster["b"]], "singles", "standard"), Promo(roster["c"])]
    rivalry = RivalryManager()
    rng_one = random.Random(42)
    rng_two = random.Random(42)
    result_one = simulator.compute_show(slots, match_types, rivalry, rng_one, 4.0)
    result_two = simulator.compute_show(slots, match_types, rivalry, rng_two, 4.0)
    assert result_one == result_two


def test_game_state_show_economy_is_deterministic() -> None:
    wrestlers, match_types = build_definitions()
    state_one = GameState(wrestlers, match_types, seed=123)
    state_two = GameState(wrestlers, match_types, seed=123)

    state_one.show_card = build_state_slots(state_one)
    state_two.show_card = build_state_slots(state_two)

    show_one = state_one.run_show()
    show_two = state_two.run_show()

    assert show_one.results == show_two.results
    assert show_one.show_rating == show_two.show_rating
    assert show_one.audience == show_two.audience
    assert show_one.gate_income == show_two.gate_income
    assert show_one.merch_income == show_two.merch_income
    assert show_one.total_earned == show_two.total_earned
    assert show_one.show_cost == show_two.show_cost
    assert state_one.money == state_two.money


def test_booking_price_helpers_match_formula() -> None:
    popularity = 50
    expected = int(
        round(
            constants.BOOKING_PRICE_BASE
            + constants.BOOKING_PRICE_A * (popularity ** constants.BOOKING_PRICE_EXPONENT)
        )
    )

    wrestler = WrestlerState("a", "A", "Face", popularity, 20, 50)

    assert wrestler.booking_price() == expected
