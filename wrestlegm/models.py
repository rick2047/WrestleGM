"""Domain models for WrestleGM."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Union

from wrestlegm import constants
Alignment = Literal["Face", "Heel"]
PairKey = tuple[str, str]


def normalize_pair(wrestler_a_id: str, wrestler_b_id: str) -> PairKey:
    """Return a normalized pair key for two wrestler IDs."""

    return (
        (wrestler_a_id, wrestler_b_id)
        if wrestler_a_id <= wrestler_b_id
        else (wrestler_b_id, wrestler_a_id)
    )


@dataclass
class WrestlerState:
    """Mutable wrestler state for the running game."""

    id: str
    name: str
    alignment: Alignment
    popularity: int
    stamina: int
    mic_skill: int

    def booking_price(self) -> int:
        """Return the booking price based on current popularity."""

        base = constants.BOOKING_PRICE_BASE
        a = constants.BOOKING_PRICE_A
        return int(round(base + a * (self.popularity ** constants.BOOKING_PRICE_EXPONENT)))


@dataclass(frozen=True)
class WrestlerDefinition:
    """Static wrestler definition loaded from data."""

    id: str
    name: str
    alignment: Alignment
    popularity: int
    stamina: int
    mic_skill: int
    description: str = ""
    avatar_path: str = ""




@dataclass(frozen=True)
class MatchTypeModifiers:
    """Simulation modifiers for a match type."""

    outcome_chaos: float
    rating_bonus: int
    rating_variance: int
    stamina_cost_winner: int
    stamina_cost_loser: int
    popularity_delta_winner: int
    popularity_delta_loser: int


@dataclass(frozen=True)
class MatchTypeDefinition:
    """Static match type definition loaded from data."""

    id: str
    name: str
    description: str
    modifiers: MatchTypeModifiers
    base_cost: int = 0


@dataclass(frozen=True)
class MatchCategory:
    """Static match category definition for wrestler count."""

    id: int
    name: str
    size: int


MATCH_CATEGORIES: list[MatchCategory] = [
    MatchCategory(id=1, name="Singles", size=2),
    MatchCategory(id=2, name="Triple Threat", size=3),
    MatchCategory(id=3, name="Fatal 4-Way", size=4),
]


@dataclass(frozen=True)
class Match:
    """Booked match within a show."""

    wrestlers: List[WrestlerState]
    match_category: MatchCategory
    match_type_id: str

    @property
    def wrestler_ids(self) -> List[str]:
        return [wrestler.id for wrestler in self.wrestlers]

    @property
    def match_category_id(self) -> int:
        return self.match_category.id


@dataclass(frozen=True)
class Promo:
    """Booked promo within a show."""

    wrestler: WrestlerState

    @property
    def wrestler_id(self) -> str:
        return self.wrestler.id


@dataclass(frozen=True)
class RivalryState:
    """Pairwise rivalry state between two wrestlers."""

    wrestler_a_id: str
    wrestler_b_id: str
    rivalry_value: int


@dataclass(frozen=True)
class CooldownState:
    """Pairwise cooldown state between two wrestlers."""

    wrestler_a_id: str
    wrestler_b_id: str
    remaining_shows: int


@dataclass(frozen=True)
class StatDelta:
    """Per-wrestler stat change from a match."""

    popularity: int
    stamina: int


@dataclass(frozen=True)
class MatchResult:
    """Immutable result of a simulated match."""

    winner_id: str
    non_winner_ids: List[str]
    rating: float
    match_category: MatchCategory
    match_type_id: str
    applied_modifiers: MatchTypeModifiers
    stat_deltas: Dict[str, StatDelta]

    @property
    def match_category_id(self) -> int:
        return self.match_category.id


@dataclass(frozen=True)
class PromoResult:
    """Immutable result of a simulated promo."""

    wrestler_id: str
    rating: float
    stat_deltas: Dict[str, StatDelta]


ShowSlot = Union[Match, Promo]
ShowResult = Union[MatchResult, PromoResult]


@dataclass
class Show:
    """Show state and results."""

    show_index: int
    scheduled_slots: List[ShowSlot]
    results: List[ShowResult]
    show_rating: float | None = None
    audience: int | None = None
    gate_income: int | None = None
    merch_income: int | None = None
    total_earned: int | None = None
    show_cost: int | None = None
