"""Deterministic simulation logic for WrestleGM."""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Dict, Iterable, List

from wrestlegm import constants
from wrestlegm.models import Match, MatchResult, MatchTypeDefinition, MatchTypeModifiers, StatDelta, WrestlerState


@dataclass(frozen=True)
class OutcomeDebug:
    """Debug payload for outcome simulation."""

    power_a: float
    power_b: float
    diff: float
    p_base: float
    outcome_chaos: float
    p_final: float
    r: float


@dataclass(frozen=True)
class RatingDebug:
    """Debug payload for rating simulation."""

    pop_avg: float
    sta_avg: float
    base_100: float
    alignment_mod: float
    rating_bonus: float
    rating_variance: int
    swing: int
    rating_100: float
    rating_stars: float


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp a value to a range."""

    return max(minimum, min(value, maximum))


def lerp(start: float, end: float, amount: float) -> float:
    """Linearly interpolate between two values."""

    return start + (end - start) * amount


def simulate_outcome(
    wrestler_a: WrestlerState,
    wrestler_b: WrestlerState,
    modifiers: MatchTypeModifiers,
    rng: random.Random,
) -> tuple[str, str, OutcomeDebug]:
    """Simulate the winner and loser for a match."""

    power_a = wrestler_a.popularity * constants.P_WEIGHT + wrestler_a.stamina * constants.S_WEIGHT
    power_b = wrestler_b.popularity * constants.P_WEIGHT + wrestler_b.stamina * constants.S_WEIGHT
    diff = power_a - power_b
    p_base = clamp(0.5 + diff / constants.D_SCALE, constants.P_MIN, constants.P_MAX)
    p_final = lerp(p_base, 0.5, modifiers.outcome_chaos)
    r = rng.random()
    winner_id = wrestler_a.id if r < p_final else wrestler_b.id
    loser_id = wrestler_b.id if winner_id == wrestler_a.id else wrestler_a.id
    debug = OutcomeDebug(
        power_a=power_a,
        power_b=power_b,
        diff=diff,
        p_base=p_base,
        outcome_chaos=modifiers.outcome_chaos,
        p_final=p_final,
        r=r,
    )
    return winner_id, loser_id, debug


def simulate_rating(
    wrestler_a: WrestlerState,
    wrestler_b: WrestlerState,
    match_type: MatchTypeDefinition,
    rng: random.Random,
) -> tuple[float, RatingDebug]:
    """Simulate a match rating in stars."""

    pop_avg = (wrestler_a.popularity + wrestler_b.popularity) / 2
    sta_avg = (wrestler_a.stamina + wrestler_b.stamina) / 2
    base_100 = pop_avg * constants.POP_W + sta_avg * constants.STA_W

    alignment_mod = 0.0
    if wrestler_a.alignment != wrestler_b.alignment:
        alignment_mod = constants.ALIGN_BONUS
    elif wrestler_a.alignment == "Heel" and wrestler_b.alignment == "Heel":
        alignment_mod = -2 * constants.ALIGN_BONUS

    base_100 += alignment_mod
    base_100 += match_type.modifiers.rating_bonus

    swing = rng.randint(-match_type.modifiers.rating_variance, match_type.modifiers.rating_variance)
    rating_100 = clamp(base_100 + swing, 0, 100)
    rating_stars = round((rating_100 / 100) * 5, 1)

    debug = RatingDebug(
        pop_avg=pop_avg,
        sta_avg=sta_avg,
        base_100=base_100,
        alignment_mod=alignment_mod,
        rating_bonus=match_type.modifiers.rating_bonus,
        rating_variance=match_type.modifiers.rating_variance,
        swing=swing,
        rating_100=rating_100,
        rating_stars=rating_stars,
    )
    return rating_stars, debug


def simulate_stat_deltas(
    winner_id: str,
    loser_id: str,
    modifiers: MatchTypeModifiers,
) -> Dict[str, StatDelta]:
    """Compute stat deltas for a match."""

    return {
        winner_id: StatDelta(
            popularity=modifiers.popularity_delta_winner,
            stamina=-modifiers.stamina_cost_winner,
        ),
        loser_id: StatDelta(
            popularity=modifiers.popularity_delta_loser,
            stamina=-modifiers.stamina_cost_loser,
        ),
    }


def simulate_match(
    match: Match,
    roster: Dict[str, WrestlerState],
    match_types: Dict[str, MatchTypeDefinition],
    rng: random.Random,
) -> MatchResult:
    """Run the deterministic simulation pipeline for a match."""

    wrestler_a = roster[match.wrestler_a_id]
    wrestler_b = roster[match.wrestler_b_id]
    match_type = match_types[match.match_type_id]

    winner_id, loser_id, _ = simulate_outcome(wrestler_a, wrestler_b, match_type.modifiers, rng)
    rating, _ = simulate_rating(wrestler_a, wrestler_b, match_type, rng)
    deltas = simulate_stat_deltas(winner_id, loser_id, match_type.modifiers)

    return MatchResult(
        winner_id=winner_id,
        loser_id=loser_id,
        rating=rating,
        match_type_id=match.match_type_id,
        applied_modifiers=match_type.modifiers,
        stat_deltas=deltas,
    )


def simulate_show(
    matches: Iterable[Match],
    roster: Dict[str, WrestlerState],
    match_types: Dict[str, MatchTypeDefinition],
    rng: random.Random,
) -> List[MatchResult]:
    """Simulate all matches in a show in card order."""

    return [simulate_match(match, roster, match_types, rng) for match in matches]


def aggregate_show_rating(results: Iterable[MatchResult]) -> float:
    """Compute the arithmetic mean of match ratings."""

    ratings = [result.rating for result in results]
    if not ratings:
        return 0.0
    return sum(ratings) / len(ratings)
