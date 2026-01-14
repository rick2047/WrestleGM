"""Deterministic simulation logic for WrestleGM."""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Callable, Dict, Iterable, List

from wrestlegm import constants
from wrestlegm.models import (
    Match,
    MatchResult,
    MatchTypeDefinition,
    MatchTypeModifiers,
    Promo,
    PromoResult,
    ShowResult,
    ShowSlot,
    StatDelta,
    WrestlerState,
)


@dataclass(frozen=True)
class OutcomeDebug:
    """Debug payload for outcome simulation."""

    powers: List[float]
    p_base: List[float]
    outcome_chaos: float
    p_final: List[float]
    r: float
    winner_id: str


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


@dataclass(frozen=True)
class PromoRatingDebug:
    """Debug payload for promo rating simulation."""

    base_100: float
    swing: int
    rating_100: float
    rating_stars: float


@dataclass(frozen=True)
class RivalryRatingContext:
    """Context for rivalry-based rating adjustments."""

    active_pairs: int = 0
    blowoff_pairs: int = 0
    has_cooldown: bool = False


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp a value to a range."""

    return max(minimum, min(value, maximum))


def lerp(start: float, end: float, amount: float) -> float:
    """Linearly interpolate between two values."""

    return start + (end - start) * amount


def apply_rivalry_adjustments(rating: float, context: RivalryRatingContext) -> float:
    """Apply rivalry bonuses and cooldown penalties to a star rating."""

    rating += context.active_pairs * constants.RIVALRY_BONUS
    rating += context.blowoff_pairs * constants.BLOWOFF_BONUS
    if context.has_cooldown:
        rating -= constants.COOLDOWN_PENALTY
    return clamp(rating, 0.0, 5.0)


class SimulationEngine:
    """Deterministic simulation engine owning RNG and pipeline steps."""

    def __init__(self, seed: int = 1337) -> None:
        """Initialize the engine with a deterministic RNG seed."""

        self.seed = seed
        self.rng = random.Random(seed)

    def simulate_outcome(
        self,
        wrestlers: List[WrestlerState],
        modifiers: MatchTypeModifiers,
    ) -> tuple[str, List[str], OutcomeDebug]:
        """Simulate the winner and non-winners for a match."""

        if not wrestlers:
            raise ValueError("Cannot simulate outcome without wrestlers.")

        powers = [
            wrestler.popularity * constants.P_WEIGHT + wrestler.stamina * constants.S_WEIGHT
            for wrestler in wrestlers
        ]
        total_power = sum(powers)
        if total_power <= 0:
            p_base = [1 / len(wrestlers)] * len(wrestlers)
        else:
            p_base = [power / total_power for power in powers]

        uniform = 1 / len(wrestlers)
        p_final = [lerp(p, uniform, modifiers.outcome_chaos) for p in p_base]
        final_total = sum(p_final)
        if final_total <= 0:
            p_final = [uniform] * len(wrestlers)
        else:
            p_final = [p / final_total for p in p_final]

        r = self.rng.random()
        cumulative = 0.0
        winner_index = len(wrestlers) - 1
        for index, probability in enumerate(p_final):
            cumulative += probability
            if r <= cumulative:
                winner_index = index
                break

        winner_id = wrestlers[winner_index].id
        non_winner_ids = [
            wrestler.id for index, wrestler in enumerate(wrestlers) if index != winner_index
        ]
        debug = OutcomeDebug(
            powers=powers,
            p_base=p_base,
            outcome_chaos=modifiers.outcome_chaos,
            p_final=p_final,
            r=r,
            winner_id=winner_id,
        )
        return winner_id, non_winner_ids, debug

    def simulate_rating(
        self,
        wrestlers: List[WrestlerState],
        match_type: MatchTypeDefinition,
    ) -> tuple[float, RatingDebug]:
        """Simulate a match rating in stars."""

        if not wrestlers:
            raise ValueError("Cannot simulate rating without wrestlers.")

        pop_avg = sum(w.popularity for w in wrestlers) / len(wrestlers)
        sta_avg = sum(w.stamina for w in wrestlers) / len(wrestlers)
        base_100 = pop_avg * constants.POP_W + sta_avg * constants.STA_W

        faces = sum(1 for w in wrestlers if w.alignment == "Face")
        heels = len(wrestlers) - faces
        if len(wrestlers) == 2:
            if faces == 1 and heels == 1:
                alignment_mod = constants.ALIGN_BONUS
            elif heels == 2:
                alignment_mod = -2 * constants.ALIGN_BONUS
            else:
                alignment_mod = 0.0
        elif heels == len(wrestlers):
            alignment_mod = -2 * constants.ALIGN_BONUS
        elif faces == len(wrestlers):
            alignment_mod = 0.0
        elif heels > faces:
            alignment_mod = constants.ALIGN_BONUS
        elif heels == faces:
            alignment_mod = 0.0
        else:
            alignment_mod = -constants.ALIGN_BONUS

        base_100 += alignment_mod
        base_100 += match_type.modifiers.rating_bonus

        swing = self.rng.randint(
            -match_type.modifiers.rating_variance,
            match_type.modifiers.rating_variance,
        )
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
        self,
        winner_id: str,
        non_winner_ids: List[str],
        modifiers: MatchTypeModifiers,
    ) -> Dict[str, StatDelta]:
        """Compute stat deltas for a match."""

        deltas = {
            winner_id: StatDelta(
                popularity=modifiers.popularity_delta_winner,
                stamina=-modifiers.stamina_cost_winner,
            )
        }
        for wrestler_id in non_winner_ids:
            deltas[wrestler_id] = StatDelta(
                popularity=modifiers.popularity_delta_loser,
                stamina=-modifiers.stamina_cost_loser,
            )
        return deltas

    def simulate_promo_rating(
        self,
        wrestler: WrestlerState,
    ) -> tuple[float, float, PromoRatingDebug]:
        """Simulate a promo rating in stars and return quality in 0-100 space."""

        base_100 = wrestler.mic_skill * 0.7 + wrestler.popularity * 0.3
        swing = self.rng.randint(-constants.PROMO_VARIANCE, constants.PROMO_VARIANCE)
        rating_100 = clamp(base_100 + swing, 0, 100)
        rating_stars = round((rating_100 / 100) * 5, 1)
        debug = PromoRatingDebug(
            base_100=base_100,
            swing=swing,
            rating_100=rating_100,
            rating_stars=rating_stars,
        )
        return rating_stars, rating_100, debug

    def simulate_promo_deltas(self, rating_100: float) -> StatDelta:
        """Compute stat deltas for a promo."""

        pop_delta = 5 if rating_100 >= 50 else -5
        stamina_delta = constants.STAMINA_RECOVERY_PER_SHOW // 2
        return StatDelta(
            popularity=pop_delta,
            stamina=stamina_delta,
        )

    def simulate_match(
        self,
        match: Match,
        roster: Dict[str, WrestlerState],
        match_types: Dict[str, MatchTypeDefinition],
        rivalry_context: RivalryRatingContext | None = None,
    ) -> MatchResult:
        """Run the deterministic simulation pipeline for a match."""

        match_type = match_types[match.match_type_id]
        wrestlers = [roster[wrestler_id] for wrestler_id in match.wrestler_ids]

        winner_id, non_winner_ids, _ = self.simulate_outcome(
            wrestlers,
            match_type.modifiers,
        )
        rating, _ = self.simulate_rating(wrestlers, match_type)
        if rivalry_context is not None:
            rating = apply_rivalry_adjustments(rating, rivalry_context)
        deltas = self.simulate_stat_deltas(
            winner_id,
            non_winner_ids,
            match_type.modifiers,
        )

        return MatchResult(
            winner_id=winner_id,
            non_winner_ids=non_winner_ids,
            rating=rating,
            match_category_id=match.match_category_id,
            match_type_id=match.match_type_id,
            applied_modifiers=match_type.modifiers,
            stat_deltas=deltas,
        )

    def simulate_promo(
        self,
        promo: Promo,
        roster: Dict[str, WrestlerState],
    ) -> PromoResult:
        """Run the deterministic simulation pipeline for a promo."""

        wrestler = roster[promo.wrestler_id]
        rating, rating_100, _ = self.simulate_promo_rating(wrestler)
        deltas = self.simulate_promo_deltas(rating_100)
        deltas = {promo.wrestler_id: deltas}
        return PromoResult(
            wrestler_id=promo.wrestler_id,
            rating=rating,
            stat_deltas=deltas,
        )

    def simulate_show(
        self,
        slots: Iterable[ShowSlot],
        roster: Dict[str, WrestlerState],
        match_types: Dict[str, MatchTypeDefinition],
        rivalry_context_provider: Callable[[Match], RivalryRatingContext] | None = None,
    ) -> List[ShowResult]:
        """Simulate all slots in a show in card order."""

        results: List[ShowResult] = []
        for slot in slots:
            if isinstance(slot, Match):
                context = None
                if rivalry_context_provider is not None:
                    context = rivalry_context_provider(slot)
                results.append(self.simulate_match(slot, roster, match_types, context))
            else:
                results.append(self.simulate_promo(slot, roster))
        return results

    def aggregate_show_rating(self, results: Iterable[ShowResult]) -> float:
        """Compute the arithmetic mean of slot ratings."""

        ratings = [result.rating for result in results]
        if not ratings:
            return 0.0
        return sum(ratings) / len(ratings)
