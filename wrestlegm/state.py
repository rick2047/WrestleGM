"""In-memory game state for WrestleGM."""

from __future__ import annotations

import random
from typing import Dict, Iterable, List, Optional

from wrestlegm import constants
from wrestlegm.models import Match, MatchResult, MatchTypeDefinition, Show, StatDelta, WrestlerDefinition, WrestlerState
from wrestlegm.sim import aggregate_show_rating, simulate_show


class GameState:
    """Primary state container and rules for the MVP."""

    def __init__(
        self,
        wrestlers: Iterable[WrestlerDefinition],
        match_types: Iterable[MatchTypeDefinition],
        seed: int = 1337,
    ) -> None:
        self.seed = seed
        self.rng = random.Random(seed)
        self.roster: Dict[str, WrestlerState] = {
            wrestler.id: WrestlerState(
                id=wrestler.id,
                name=wrestler.name,
                alignment=wrestler.alignment,
                popularity=wrestler.popularity,
                stamina=wrestler.stamina,
            )
            for wrestler in wrestlers
        }
        self.match_types: Dict[str, MatchTypeDefinition] = {
            match_type.id: match_type for match_type in match_types
        }
        self.show_index = 1
        self.show_card: List[Optional[Match]] = [None] * constants.SHOW_MATCH_COUNT
        self.last_show: Show | None = None

    def clear_slot(self, slot_index: int) -> None:
        """Clear a match slot."""

        self.show_card[slot_index] = None

    def set_slot(self, slot_index: int, match: Match) -> None:
        """Set a match slot after validation."""

        errors = self.validate_match(match, slot_index=slot_index)
        if errors:
            raise ValueError(
                "Invalid match: " + ", ".join(errors)
            )
        self.show_card[slot_index] = match

    def validate_match(self, match: Match, slot_index: int | None = None) -> List[str]:
        """Return validation errors for a match in a slot."""

        errors: List[str] = []
        if match.wrestler_a_id == match.wrestler_b_id:
            errors.append("duplicate_wrestler")
        if match.wrestler_a_id not in self.roster or match.wrestler_b_id not in self.roster:
            errors.append("unknown_wrestler")
        if match.match_type_id not in self.match_types:
            errors.append("unknown_match_type")

        for wrestler_id in (match.wrestler_a_id, match.wrestler_b_id):
            if wrestler_id not in self.roster:
                continue
            if self.is_wrestler_booked(wrestler_id, exclude_slot=slot_index):
                errors.append("already_booked")
                break
            if self.roster[wrestler_id].stamina <= constants.STAMINA_MIN_BOOKABLE:
                errors.append("not_enough_stamina")
                break
        return errors

    def is_wrestler_booked(self, wrestler_id: str, exclude_slot: int | None = None) -> bool:
        """Check whether a wrestler is already booked in the show card."""

        for index, match in enumerate(self.show_card):
            if match is None:
                continue
            if exclude_slot is not None and index == exclude_slot:
                continue
            if wrestler_id in (match.wrestler_a_id, match.wrestler_b_id):
                return True
        return False

    def validate_show(self) -> List[str]:
        """Return validation errors for the full show card."""

        errors: List[str] = []
        if any(match is None for match in self.show_card):
            errors.append("incomplete")
            return errors

        seen: set[str] = set()
        for index, match in enumerate(self.show_card):
            assert match is not None
            errors.extend(self.validate_match(match, slot_index=index))
            for wrestler_id in (match.wrestler_a_id, match.wrestler_b_id):
                if wrestler_id in seen:
                    errors.append("duplicate_wrestler")
                seen.add(wrestler_id)
        return errors

    def run_show(self) -> Show:
        """Simulate the current show, apply deltas, and advance."""

        errors = self.validate_show()
        if errors:
            raise ValueError("Show is invalid: " + ", ".join(errors))

        matches = [match for match in self.show_card if match is not None]
        show = Show(show_index=self.show_index, scheduled_matches=matches, results=[])
        results = simulate_show(matches, self.roster, self.match_types, self.rng)
        show.results = results
        show.show_rating = aggregate_show_rating(results)
        self.apply_show_results(show)
        self.last_show = show
        self.show_index += 1
        self.show_card = [None] * constants.SHOW_MATCH_COUNT
        return show

    def apply_show_results(self, show: Show) -> None:
        """Apply all stat deltas and recovery for a completed show."""

        aggregated: Dict[str, StatDelta] = {}
        participants: set[str] = set()

        for result in show.results:
            participants.add(result.winner_id)
            participants.add(result.loser_id)
            for wrestler_id, delta in result.stat_deltas.items():
                current = aggregated.get(wrestler_id, StatDelta(popularity=0, stamina=0))
                aggregated[wrestler_id] = StatDelta(
                    popularity=current.popularity + delta.popularity,
                    stamina=current.stamina + delta.stamina,
                )

        new_values: Dict[str, WrestlerState] = {}
        for wrestler_id, wrestler in self.roster.items():
            delta = aggregated.get(wrestler_id, StatDelta(popularity=0, stamina=0))
            pop = max(0, min(100, wrestler.popularity + delta.popularity))
            sta = max(0, min(100, wrestler.stamina + delta.stamina))
            new_values[wrestler_id] = WrestlerState(
                id=wrestler.id,
                name=wrestler.name,
                alignment=wrestler.alignment,
                popularity=pop,
                stamina=sta,
            )

        for wrestler_id, wrestler in new_values.items():
            self.roster[wrestler_id] = wrestler

        for wrestler_id, wrestler in self.roster.items():
            if wrestler_id in participants:
                continue
            recovered = min(100, wrestler.stamina + constants.STAMINA_RECOVERY_PER_SHOW)
            self.roster[wrestler_id].stamina = recovered
