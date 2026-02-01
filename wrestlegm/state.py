"""In-memory game state for WrestleGM."""

from __future__ import annotations

from typing import Dict, Iterable, List

from wrestlegm import constants
from wrestlegm.economy import EconomySimulator
from wrestlegm.models import (
    Match,
    MATCH_CATEGORIES,
    MatchTypeDefinition,
    Promo,
    PromoResult,
    Show,
    ShowResult,
    ShowSlot,
    StatDelta,
    WrestlerDefinition,
    WrestlerState,
)
from wrestlegm.sim import SimulationEngine
from wrestlegm.rivalries import RivalryManager


class GameState:
    """Primary state container and rules for the MVP."""

    def __init__(
        self,
        wrestlers: Iterable[WrestlerDefinition],
        match_types: Iterable[MatchTypeDefinition],
        seed: int = 1337,
    ) -> None:
        self._wrestler_defs = list(wrestlers)
        self._match_type_defs = list(match_types)
        self._default_seed = seed
        self._reset_game_state(self._wrestler_defs, self._match_type_defs, seed)

    def _reset_game_state(
        self,
        wrestlers: Iterable[WrestlerDefinition],
        match_types: Iterable[MatchTypeDefinition],
        seed: int,
    ) -> None:
        """Reset state for a fresh session or after loading."""

        self.engine = SimulationEngine(seed=seed)
        self.applier = ShowApplier()
        self.wrestler_defs = {wrestler.id: wrestler for wrestler in wrestlers}
        self.roster = {
            wrestler.id: WrestlerState(
                id=wrestler.id,
                name=wrestler.name,
                alignment=wrestler.alignment,
                popularity=wrestler.popularity,
                stamina=wrestler.stamina,
                mic_skill=wrestler.mic_skill,
            )
            for wrestler in wrestlers
        }
        self.match_types = {match_type.id: match_type for match_type in match_types}
        self.rivalry_manager = RivalryManager()
        self.economy_simulator = EconomySimulator()
        self.show_index = 1
        self.show_card = [None] * constants.SHOW_SLOT_COUNT
        self.last_show = None
        self.money = constants.STARTING_MONEY

    def clear_slot(self, slot_index: int) -> None:
        """Clear a show slot."""

        self.show_card[slot_index] = None

    def set_slot(self, slot_index: int, slot: ShowSlot) -> None:
        """Set a slot after validation."""

        errors = self.validate_slot(slot, slot_index=slot_index)
        if errors:
            raise ValueError(
                "Invalid slot: " + ", ".join(errors)
            )
        self.show_card[slot_index] = slot

    def slot_type(self, slot_index: int) -> str:
        """Return the expected slot type for an index."""

        return constants.SHOW_SLOT_TYPES[slot_index]

    def validate_match(self, match: Match, slot_index: int | None = None) -> List[str]:
        """Return validation errors for a match in a slot."""

        errors: List[str] = []
        category = match.match_category
        if category not in MATCH_CATEGORIES:
            errors.append("unknown_match_category")
        if match.match_type_id not in self.match_types:
            errors.append("unknown_match_type")
        if len(set(match.wrestler_ids)) != len(match.wrestler_ids):
            errors.append("duplicate_wrestler")
        for wrestler_id in match.wrestler_ids:
            if wrestler_id not in self.roster:
                errors.append("unknown_wrestler")
                break

        if category is not None and len(match.wrestler_ids) != category.size:
            errors.append("invalid_wrestler_count")

        for wrestler_id in match.wrestler_ids:
            if wrestler_id not in self.roster:
                continue
            if self.is_wrestler_booked(wrestler_id, exclude_slot=slot_index):
                errors.append("already_booked")
                break
            if self.roster[wrestler_id].stamina <= constants.STAMINA_MIN_BOOKABLE:
                errors.append("not_enough_stamina")
                break
        return errors

    def validate_promo(self, promo: Promo, slot_index: int | None = None) -> List[str]:
        """Return validation errors for a promo in a slot."""

        errors: List[str] = []
        if promo.wrestler_id not in self.roster:
            errors.append("unknown_wrestler")
            return errors
        if self.is_wrestler_booked(promo.wrestler_id, exclude_slot=slot_index):
            errors.append("already_booked")
        return errors

    def validate_slot(self, slot: ShowSlot, slot_index: int | None = None) -> List[str]:
        """Return validation errors for a slot entry."""

        errors: List[str] = []
        if slot_index is not None:
            expected = self.slot_type(slot_index)
            if expected == "match" and not isinstance(slot, Match):
                errors.append("slot_type_mismatch")
            if expected == "promo" and not isinstance(slot, Promo):
                errors.append("slot_type_mismatch")
        if isinstance(slot, Match):
            errors.extend(self.validate_match(slot, slot_index=slot_index))
        else:
            errors.extend(self.validate_promo(slot, slot_index=slot_index))
        return errors

    def is_wrestler_booked(self, wrestler_id: str, exclude_slot: int | None = None) -> bool:
        """Check whether a wrestler is already booked in the show card."""

        for index, slot in enumerate(self.show_card):
            if slot is None:
                continue
            if exclude_slot is not None and index == exclude_slot:
                continue
            if isinstance(slot, Match):
                if wrestler_id in slot.wrestler_ids:
                    return True
            else:
                if wrestler_id == slot.wrestler_id:
                    return True
        return False

    def validate_show(self) -> List[str]:
        """Return validation errors for the full show card."""

        errors: List[str] = []
        if any(slot is None for slot in self.show_card):
            errors.append("incomplete")
            return errors

        seen: set[str] = set()
        for index, slot in enumerate(self.show_card):
            assert slot is not None
            errors.extend(self.validate_slot(slot, slot_index=index))
            if isinstance(slot, Match):
                wrestler_ids = tuple(slot.wrestler_ids)
            else:
                wrestler_ids = (slot.wrestler_id,)
            for wrestler_id in wrestler_ids:
                if wrestler_id in seen:
                    errors.append("duplicate_wrestler")
                seen.add(wrestler_id)
        return errors

    def run_show(self) -> Show:
        """Simulate the current show, apply deltas, and advance."""

        errors = self.validate_show()
        if errors:
            raise ValueError("Show is invalid: " + ", ".join(errors))

        slots: List[ShowSlot] = [slot for slot in self.show_card if slot is not None]
        show = Show(show_index=self.show_index, scheduled_slots=slots, results=[])
        results = self.engine.simulate_show(
            slots,
            self.match_types,
            rivalry_context_provider=self.rivalry_manager.rivalry_context_for_match,
        )
        show.results = results
        show.show_rating = self.engine.aggregate_show_rating(results)
        economy_result = self.economy_simulator.compute_show(
            slots,
            self.match_types,
            self.rivalry_manager,
            self.engine.rng,
            show.show_rating,
        )
        show.audience = economy_result.audience
        show.gate_income = economy_result.gate_income
        show.merch_income = economy_result.merch_income
        show.total_earned = economy_result.total_earned
        show.show_cost = economy_result.show_cost
        self.money = self.money - economy_result.show_cost + economy_result.total_earned
        self.applier.apply(show, self.roster)
        self.rivalry_manager.advance(show)
        self.last_show = show
        self.show_index += 1
        self.show_card = [None] * constants.SHOW_SLOT_COUNT
        return show

    def apply_show_results(self, show: Show) -> None:
        """Apply all stat deltas and recovery for a completed show."""

        self.applier.apply(show, self.roster)
        self.rivalry_manager.advance(show)

    def rivalry_value_for_pair(self, wrestler_a_id: str, wrestler_b_id: str) -> int:
        """Return the current rivalry value for a pair, or 0 if none."""

        return self.rivalry_manager.rivalry_value_for_pair(wrestler_a_id, wrestler_b_id)

    def cooldown_remaining_for_pair(self, wrestler_a_id: str, wrestler_b_id: str) -> int:
        """Return remaining cooldown shows for a pair, or 0 if none."""

        return self.rivalry_manager.cooldown_remaining_for_pair(wrestler_a_id, wrestler_b_id)

    def rivalry_emojis_for_match(self, wrestler_ids: Iterable[str]) -> str:
        """Return rivalry/cooldown emojis for the ordered wrestler pairs."""

        return self.rivalry_manager.rivalry_emojis_for_match(wrestler_ids)

    def rivalry_summary_for_match(self, wrestler_ids: Iterable[str]) -> str:
        """Return aggregated rivalry emojis with ASCII counts for a match."""

        return self.rivalry_manager.rivalry_summary_for_match(wrestler_ids)

    def rivalry_and_cooldown_summary_for_match(self, wrestler_ids: Iterable[str]) -> str:
        """Return aggregated rivalry and cooldown emojis with ASCII counts for a match."""

        return self.rivalry_manager.rivalry_and_cooldown_summary_for_match(wrestler_ids)

    def rivalry_emoji_for_pair(self, wrestler_a_id: str, wrestler_b_id: str) -> str:
        """Return rivalry emoji for a pair, ignoring cooldowns."""

        return self.rivalry_manager.rivalry_emoji_for_pair(wrestler_a_id, wrestler_b_id)

    def wrestler_booking_price(self, wrestler_id: str) -> int:
        """Return the booking price for a wrestler by id."""

        wrestler = self.roster.get(wrestler_id)
        if wrestler is None:
            raise KeyError(f"Unknown wrestler: {wrestler_id}")
        return wrestler.booking_price()

    def match_type_base_cost(self, match_type_id: str) -> int:
        """Return the base cost for a match type id."""

        match_type = self.match_types.get(match_type_id)
        return match_type.base_cost if match_type is not None else 0

    def current_show_cost(self) -> int:
        """Return the cost for the currently booked slots."""

        slots: List[ShowSlot] = [slot for slot in self.show_card if slot is not None]
        return self.economy_simulator.show_cost(slots, self.match_types)

    def is_bankrupt(self) -> bool:
        """Return True if the promotion has run out of money."""

        return self.money <= 0


class ShowApplier:
    """Apply match deltas, recovery, and clamping to roster state."""

    def apply(self, show: Show, roster: Dict[str, WrestlerState]) -> None:
        """Apply deltas and recovery to the roster in-place."""

        aggregated: Dict[str, StatDelta] = {}
        participants: set[str] = set()

        for result in show.results:
            if isinstance(result, PromoResult):
                participants.add(result.wrestler_id)
            else:
                participants.add(result.winner_id)
                participants.update(result.non_winner_ids)
            for wrestler_id, delta in result.stat_deltas.items():
                current = aggregated.get(wrestler_id, StatDelta(popularity=0, stamina=0))
                aggregated[wrestler_id] = StatDelta(
                    popularity=current.popularity + delta.popularity,
                    stamina=current.stamina + delta.stamina,
                )

        new_values: Dict[str, WrestlerState] = {}
        for wrestler_id, wrestler in roster.items():
            delta = aggregated.get(wrestler_id, StatDelta(popularity=0, stamina=0))
            pop = max(0, min(100, wrestler.popularity + delta.popularity))
            sta = max(0, min(100, wrestler.stamina + delta.stamina))
            new_values[wrestler_id] = WrestlerState(
                id=wrestler.id,
                name=wrestler.name,
                alignment=wrestler.alignment,
                popularity=pop,
                stamina=sta,
                mic_skill=wrestler.mic_skill,
            )

        for wrestler_id, wrestler in new_values.items():
            roster[wrestler_id] = wrestler

        for wrestler_id, wrestler in roster.items():
            if wrestler_id in participants:
                continue
            recovered = min(100, wrestler.stamina + constants.STAMINA_RECOVERY_PER_SHOW)
            roster[wrestler_id].stamina = recovered
