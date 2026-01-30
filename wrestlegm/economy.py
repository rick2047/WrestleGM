"""Economy calculations for WrestleGM."""

from __future__ import annotations

import math
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


def wrestler_booking_price(popularity: int) -> int:
    """Return the booking price for a wrestler based on popularity."""

    base = constants.BOOKING_PRICE_BASE
    a = constants.BOOKING_PRICE_A
    return int(round(base + a * (popularity ** constants.BOOKING_PRICE_EXPONENT)))


def unique_wrestler_ids(slots: Iterable[ShowSlot]) -> set[str]:
    """Return the unique wrestler ids booked on the card."""

    ids: set[str] = set()
    for slot in slots:
        if isinstance(slot, Match):
            ids.update(slot.wrestler_ids)
        else:
            ids.add(slot.wrestler_id)
    return ids


def show_cost(slots: Iterable[ShowSlot], roster: dict[str, WrestlerState], match_types: dict[str, MatchTypeDefinition]) -> int:
    """Compute the total show cost for the given slots."""

    cost = 0
    for wrestler_id in unique_wrestler_ids(slots):
        wrestler = roster[wrestler_id]
        cost += wrestler_booking_price(wrestler.popularity)

    for slot in slots:
        if isinstance(slot, Match):
            match_type = match_types.get(slot.match_type_id)
            if match_type is not None:
                cost += match_type.base_cost
    return cost


def economy_inputs_for_slots(
    slots: Iterable[ShowSlot],
    roster: dict[str, WrestlerState],
    rivalry_manager: RivalryManager,
) -> EconomyInputs:
    """Compute economy inputs for a show card."""

    booked_ids = unique_wrestler_ids(slots)
    pop_sum = sum(roster[wrestler_id].popularity for wrestler_id in booked_ids)

    align_score = 0
    rivalry_count = 0
    cooldown_count = 0

    for slot in slots:
        if not isinstance(slot, Match):
            continue
        wrestlers = [roster[wrestler_id] for wrestler_id in slot.wrestler_ids]
        for wrestler_a, wrestler_b in ordered_pairs([w.id for w in wrestlers]):
            if roster[wrestler_a].alignment != roster[wrestler_b].alignment:
                align_score += 1

        match_rivalry, match_cooldown = rivalry_manager.count_rivalry_and_cooldown_pairs(slot.wrestler_ids)
        rivalry_count += match_rivalry
        cooldown_count += match_cooldown

    return EconomyInputs(
        pop_sum=pop_sum,
        align_score=align_score,
        rivalry_count=rivalry_count,
        cooldown_count=cooldown_count,
    )


def _curve_bonus(value: int, scale: int) -> float:
    """Return a curved bonus using a square-root scale."""

    if value <= 0:
        return 0.0
    return math.sqrt(value) * scale


def compute_audience(inputs: EconomyInputs, rng_multiplier: float) -> int:
    """Compute audience size using inputs and RNG multiplier."""

    base = inputs.pop_sum * constants.AUDIENCE_POP_MULTIPLIER
    bonus = _curve_bonus(inputs.align_score, constants.AUDIENCE_ALIGN_BONUS)
    bonus += _curve_bonus(inputs.rivalry_count, constants.AUDIENCE_RIVALRY_BONUS)
    penalty = _curve_bonus(inputs.cooldown_count, constants.AUDIENCE_COOLDOWN_PENALTY)
    raw = (base + bonus - penalty) * rng_multiplier
    return max(0, int(round(raw)))


def merch_rate(show_rating: float) -> float:
    """Return the merch conversion rate from show rating."""

    rate = (
        constants.MERCH_RATE_MIN
        + constants.MERCH_RATE_LINEAR * show_rating
        + constants.MERCH_RATE_QUAD * (show_rating ** 2)
    )
    return max(constants.MERCH_RATE_MIN, min(constants.MERCH_RATE_MAX, rate))


def compute_economy(
    slots: Iterable[ShowSlot],
    roster: dict[str, WrestlerState],
    match_types: dict[str, MatchTypeDefinition],
    rivalry_manager: RivalryManager,
    rng,
    show_rating: float,
) -> EconomyResult:
    """Compute show economy values using the provided RNG."""

    cost = show_cost(slots, roster, match_types)
    inputs = economy_inputs_for_slots(slots, roster, rivalry_manager)
    audience_multiplier = rng.uniform(constants.ECONOMY_RNG_MIN, constants.ECONOMY_RNG_MAX)
    audience = compute_audience(inputs, audience_multiplier)

    gate_income = int(round(audience * constants.GATE_RATE))

    merch_multiplier = rng.uniform(constants.ECONOMY_RNG_MIN, constants.ECONOMY_RNG_MAX)
    merch_income = int(round(audience * merch_rate(show_rating) * merch_multiplier))

    total_earned = gate_income + merch_income
    return EconomyResult(
        show_cost=cost,
        audience=audience,
        gate_income=gate_income,
        merch_income=merch_income,
        total_earned=total_earned,
    )

