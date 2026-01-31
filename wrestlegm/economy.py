"""Economy calculations for WrestleGM."""

from __future__ import annotations

import math
from itertools import product
from dataclasses import dataclass
from typing import Iterable

from wrestlegm import constants
from wrestlegm.models import Match, MatchTypeDefinition, Promo, ShowSlot, WrestlerState
from wrestlegm.rivalries import RivalryManager, ordered_pairs


@dataclass(frozen=True)
class EconomyInputs:
    """Inputs for audience calculation."""

    pop_sum: int
    align_score: int
    rivalry_count: int
    cooldown_count: int


@dataclass(frozen=True)
class EconomyResult:
    """Computed economy values for a show."""

    show_cost: int
    audience: int
    gate_income: int
    merch_income: int
    total_earned: int


def _unique_wrestlers(slots: Iterable[ShowSlot]) -> dict[str, WrestlerState]:
    """Return unique wrestlers booked on the card keyed by id."""

    booked: dict[str, WrestlerState] = {}
    for slot in slots:
        if isinstance(slot, Match):
            for wrestler in slot.wrestlers:
                booked[wrestler.id] = wrestler
        else:
            booked[slot.wrestler.id] = slot.wrestler
    return booked


def _curve_bonus(value: int, scale: int) -> float:
    """Return a curved bonus using a square-root scale."""

    if value <= 0:
        return 0.0
    return math.sqrt(value) * scale


class EconomySimulator:
    """Stateless economy calculator for show outcomes."""

    def show_cost(
        self,
        slots: Iterable[ShowSlot],
        match_types: dict[str, MatchTypeDefinition],
    ) -> int:
        """Compute the total show cost for the given slots."""

        cost = 0
        for wrestler in _unique_wrestlers(slots).values():
            cost += wrestler.booking_price()

        for slot in slots:
            if isinstance(slot, Match):
                match_type = match_types.get(slot.match_type_id)
                if match_type is not None:
                    cost += match_type.base_cost
        return cost

    def audience_inputs_for_slots(
        self,
        slots: Iterable[ShowSlot],
        rivalry_manager: RivalryManager,
    ) -> EconomyInputs:
        """Compute economy inputs for a show card."""

        booked = _unique_wrestlers(slots)
        pop_sum = sum(wrestler.popularity for wrestler in booked.values())

        align_score = 0
        rivalry_count = 0
        cooldown_count = 0

        for slot in slots:
            if not isinstance(slot, Match):
                continue
            alignment_map = {wrestler.id: wrestler.alignment for wrestler in slot.wrestlers}
            for wrestler_a, wrestler_b in ordered_pairs(slot.wrestler_ids):
                if alignment_map[wrestler_a] != alignment_map[wrestler_b]:
                    align_score += 1

            match_rivalry, match_cooldown = rivalry_manager.count_rivalry_and_cooldown_pairs(
                slot.wrestler_ids
            )
            rivalry_count += match_rivalry
            cooldown_count += match_cooldown

        return EconomyInputs(
            pop_sum=pop_sum,
            align_score=align_score,
            rivalry_count=rivalry_count,
            cooldown_count=cooldown_count,
        )

    @staticmethod
    def _compute_audience(inputs: EconomyInputs, rng_multiplier: float) -> int:
        """Compute audience size using inputs and RNG multiplier."""

        base = inputs.pop_sum * constants.AUDIENCE_POP_MULTIPLIER
        bonus = _curve_bonus(inputs.align_score, constants.AUDIENCE_ALIGN_BONUS)
        bonus += _curve_bonus(inputs.rivalry_count, constants.AUDIENCE_RIVALRY_BONUS)
        penalty = _curve_bonus(inputs.cooldown_count, constants.AUDIENCE_COOLDOWN_PENALTY)
        raw = (base + bonus - penalty) * rng_multiplier
        return max(0, int(round(raw)))

    @staticmethod
    def _merch_rate(show_rating: float) -> float:
        """Return the merch conversion rate from show rating."""

        rate = (
            constants.MERCH_RATE_MIN
            + constants.MERCH_RATE_LINEAR * show_rating
            + constants.MERCH_RATE_QUAD * (show_rating ** 2)
        )
        return max(constants.MERCH_RATE_MIN, min(constants.MERCH_RATE_MAX, rate))

    def compute_show(
        self,
        slots: Iterable[ShowSlot],
        match_types: dict[str, MatchTypeDefinition],
        rivalry_manager: RivalryManager,
        rng,
        show_rating: float,
    ) -> EconomyResult:
        """Compute show economy values using the provided RNG."""

        cost = self.show_cost(slots, match_types)
        inputs = self.audience_inputs_for_slots(slots, rivalry_manager)
        audience_multiplier = rng.uniform(constants.ECONOMY_RNG_MIN, constants.ECONOMY_RNG_MAX)
        audience = self._compute_audience(inputs, audience_multiplier)

        gate_income = int(round(audience * constants.GATE_RATE))

        merch_multiplier = rng.uniform(constants.ECONOMY_RNG_MIN, constants.ECONOMY_RNG_MAX)
        merch_income = int(round(audience * self._merch_rate(show_rating) * merch_multiplier))

        total_earned = gate_income + merch_income
        return EconomyResult(
            show_cost=cost,
            audience=audience,
            gate_income=gate_income,
            merch_income=merch_income,
            total_earned=total_earned,
        )

    def min_valid_show_cost(
        self,
        roster: dict[str, WrestlerState],
        match_types: dict[str, MatchTypeDefinition],
    ) -> int | None:
        """Return the minimum possible cost for any valid show card, or None if impossible."""

        match_types_by_category: dict[str, int] = {}
        for category_id in constants.MATCH_CATEGORY_ORDER:
            eligible = [
                match_type.base_cost
                for match_type in match_types.values()
                if match_type.allowed_categories is None
                or category_id in match_type.allowed_categories
            ]
            if not eligible:
                continue
            match_types_by_category[category_id] = min(eligible)

        if not match_types_by_category:
            return None

        match_eligible = [
            (wrestler.booking_price(), wrestler.id)
            for wrestler in roster.values()
            if wrestler.stamina > constants.STAMINA_MIN_BOOKABLE
        ]
        match_eligible.sort(key=lambda item: item[0])

        promo_eligible = [
            (wrestler.booking_price(), wrestler.id)
            for wrestler in roster.values()
        ]
        promo_eligible.sort(key=lambda item: item[0])

        min_cost: int | None = None
        category_ids = list(match_types_by_category.keys())
        match_slot_count = constants.SHOW_SLOT_TYPES.count("match")
        promo_needed = constants.SHOW_SLOT_TYPES.count("promo")

        for category_combo in product(category_ids, repeat=match_slot_count):
            match_count = sum(
                constants.MATCH_CATEGORIES[category_id]["size"]
                for category_id in category_combo
            )
            if len(match_eligible) < match_count:
                continue
            match_pick = match_eligible[:match_count]
            match_ids = {wrestler_id for _, wrestler_id in match_pick}

            remaining_promos = [
                entry for entry in promo_eligible if entry[1] not in match_ids
            ]
            if len(remaining_promos) < promo_needed:
                continue
            promo_pick = remaining_promos[:promo_needed]

            wrestler_cost = sum(cost for cost, _ in match_pick + promo_pick)
            base_cost = sum(
                match_types_by_category[category_id]
                for category_id in category_combo
            )
            total_cost = wrestler_cost + base_cost
            if min_cost is None or total_cost < min_cost:
                min_cost = total_cost
        return min_cost


def show_cost(
    slots: Iterable[ShowSlot],
    match_types: dict[str, MatchTypeDefinition],
) -> int:
    """Compute the total show cost for the given slots."""

    return EconomySimulator().show_cost(slots, match_types)


def compute_economy(
    slots: Iterable[ShowSlot],
    match_types: dict[str, MatchTypeDefinition],
    rivalry_manager: RivalryManager,
    rng,
    show_rating: float,
) -> EconomyResult:
    """Compute show economy values using the provided RNG."""

    return EconomySimulator().compute_show(
        slots,
        match_types,
        rivalry_manager,
        rng,
        show_rating,
    )
