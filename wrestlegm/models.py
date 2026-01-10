"""Domain models for WrestleGM."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal

Alignment = Literal["Face", "Heel"]


@dataclass
class WrestlerState:
    """Mutable wrestler state for the running game."""

    id: str
    name: str
    alignment: Alignment
    popularity: int
    stamina: int


@dataclass(frozen=True)
class WrestlerDefinition:
    """Static wrestler definition loaded from data."""

    id: str
    name: str
    alignment: Alignment
    popularity: int
    stamina: int


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


@dataclass(frozen=True)
class Match:
    """Booked match within a show."""

    wrestler_a_id: str
    wrestler_b_id: str
    match_type_id: str


@dataclass(frozen=True)
class StatDelta:
    """Per-wrestler stat change from a match."""

    popularity: int
    stamina: int


@dataclass(frozen=True)
class MatchResult:
    """Immutable result of a simulated match."""

    winner_id: str
    loser_id: str
    rating: float
    match_type_id: str
    applied_modifiers: MatchTypeModifiers
    stat_deltas: Dict[str, StatDelta]


@dataclass
class Show:
    """Show state and results."""

    show_index: int
    scheduled_matches: List[Match]
    results: List[MatchResult]
    show_rating: float | None = None
