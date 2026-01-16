"""In-memory game state for WrestleGM."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Optional

from wrestlegm import constants
from wrestlegm.models import (
    Match,
    MatchTypeDefinition,
    CooldownState,
    Promo,
    PromoResult,
    RivalryState,
    Show,
    ShowResult,
    ShowSlot,
    StatDelta,
    WrestlerDefinition,
    WrestlerState,
)
from wrestlegm.sim import RivalryRatingContext, SimulationEngine
from wrestlegm import persistence

PairKey = tuple[str, str]


def normalize_pair(wrestler_a_id: str, wrestler_b_id: str) -> PairKey:
    """Return a normalized pair key for two wrestler IDs."""

    return (
        (wrestler_a_id, wrestler_b_id)
        if wrestler_a_id <= wrestler_b_id
        else (wrestler_b_id, wrestler_a_id)
    )


def ordered_pairs(wrestler_ids: Iterable[str]) -> list[tuple[str, str]]:
    """Return ordered unique pairs based on the wrestler list order."""

    ids = list(wrestler_ids)
    pairs: list[tuple[str, str]] = []
    for index, wrestler_id in enumerate(ids):
        for other_id in ids[index + 1 :]:
            pairs.append((wrestler_id, other_id))
    return pairs


class GameState:
    """Primary state container and rules for the MVP."""

    def __init__(
        self,
        wrestlers: Iterable[WrestlerDefinition],
        match_types: Iterable[MatchTypeDefinition],
        seed: int = 1337,
        save_dir: Path | None = None,
    ) -> None:
        self._wrestler_defs = list(wrestlers)
        self._match_type_defs = list(match_types)
        self._default_seed = seed
        self._save_dir = save_dir
        self.current_slot_index: int | None = None
        self.pending_slot_name: str | None = None
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
        self.rivalry_states = {}
        self.cooldown_states = {}
        self.show_index = 1
        self.show_card = [None] * constants.SHOW_SLOT_COUNT
        self.last_show = None

    def new_game(self, slot_index: int, slot_name: str) -> None:
        """Start a new session and assign the active slot."""

        self._reset_game_state(
            self._wrestler_defs,
            self._match_type_defs,
            self._default_seed,
        )
        self.current_slot_index = slot_index
        self.pending_slot_name = slot_name

    def list_slots(self) -> list[persistence.SaveSlotInfo]:
        """Return slot metadata for selection screens."""

        return persistence.load_slot_index(self._save_dir)

    def save_current_slot(self) -> None:
        """Persist the current slot if one is active."""

        if self.current_slot_index is None:
            return
        slots = persistence.load_slot_index(self._save_dir)
        slot_info = next(
            (slot for slot in slots if slot.slot_index == self.current_slot_index),
            None,
        )
        slot_name = None
        if slot_info and slot_info.exists:
            slot_name = slot_info.name
        if slot_name is None:
            slot_name = self.pending_slot_name
        if slot_name is None:
            raise ValueError("save_slot_name_required")
        persistence.save_game_state(self, self.current_slot_index, slot_name, self._save_dir)
        self.pending_slot_name = None

    def load_slot(self, slot_index: int) -> None:
        """Load a saved slot into the current game state."""

        slots = persistence.load_slot_index(self._save_dir)
        slot_info = next((slot for slot in slots if slot.slot_index == slot_index), None)
        if slot_info is None or not slot_info.exists:
            raise ValueError("empty_slot")
        try:
            payload = persistence.load_save_payload(slot_index, self._save_dir)
        except FileNotFoundError as exc:
            raise ValueError("missing_save_file") from exc
        version = payload.get("version", 0)
        if version > persistence.SAVE_VERSION:
            raise ValueError("unsupported_save_version")
        state_payload = payload.get("state", {})
        self._reset_game_state(
            self._wrestler_defs,
            self._match_type_defs,
            state_payload.get("rng_seed", self._default_seed),
        )
        persistence.deserialize_game_state(self, state_payload)
        self.current_slot_index = slot_index
        self.pending_slot_name = None

    def clear_save_slot(self, slot_index: int) -> None:
        """Clear a persisted save slot and its metadata."""

        persistence.clear_save_slot(slot_index, self._save_dir)

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
        category = constants.MATCH_CATEGORIES.get(match.match_category_id)
        if category is None:
            errors.append("unknown_match_category")
        if match.match_type_id not in self.match_types:
            errors.append("unknown_match_type")
        if len(set(match.wrestler_ids)) != len(match.wrestler_ids):
            errors.append("duplicate_wrestler")
        for wrestler_id in match.wrestler_ids:
            if wrestler_id not in self.roster:
                errors.append("unknown_wrestler")
                break

        if category is not None and len(match.wrestler_ids) != category["size"]:
            errors.append("invalid_wrestler_count")

        match_type = self.match_types.get(match.match_type_id)
        if match_type is not None and match_type.allowed_categories is not None:
            if match.match_category_id not in match_type.allowed_categories:
                errors.append("invalid_match_type_category")

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
            self.roster,
            self.match_types,
            rivalry_context_provider=self._rivalry_context_for_match,
        )
        show.results = results
        show.show_rating = self.engine.aggregate_show_rating(results)
        self.applier.apply(show, self.roster)
        self._advance_rivalries(show)
        self.last_show = show
        self.show_index += 1
        self.show_card = [None] * constants.SHOW_SLOT_COUNT
        return show

    def apply_show_results(self, show: Show) -> None:
        """Apply all stat deltas and recovery for a completed show."""

        self.applier.apply(show, self.roster)
        self._advance_rivalries(show)

    def rivalry_value_for_pair(self, wrestler_a_id: str, wrestler_b_id: str) -> int:
        """Return the current rivalry value for a pair, or 0 if none."""

        key = normalize_pair(wrestler_a_id, wrestler_b_id)
        state = self.rivalry_states.get(key)
        return state.rivalry_value if state else 0

    def cooldown_remaining_for_pair(self, wrestler_a_id: str, wrestler_b_id: str) -> int:
        """Return remaining cooldown shows for a pair, or 0 if none."""

        key = normalize_pair(wrestler_a_id, wrestler_b_id)
        state = self.cooldown_states.get(key)
        return state.remaining_shows if state else 0

    def rivalry_emojis_for_match(self, wrestler_ids: Iterable[str]) -> str:
        """Return rivalry/cooldown emojis for the ordered wrestler pairs."""

        ids = [wrestler_id for wrestler_id in wrestler_ids if wrestler_id]
        if len(ids) < 2:
            return ""
        emojis: list[str] = []
        for wrestler_a_id, wrestler_b_id in ordered_pairs(ids):
            key = normalize_pair(wrestler_a_id, wrestler_b_id)
            cooldown = self.cooldown_states.get(key)
            if cooldown:
                emoji = self._cooldown_emoji(cooldown.remaining_shows)
                if emoji:
                    emojis.append(emoji)
                continue
            rivalry = self.rivalry_states.get(key)
            if rivalry and rivalry.rivalry_value > 0:
                emoji = self._rivalry_emoji(rivalry.rivalry_value)
                if emoji:
                    emojis.append(emoji)
        return "".join(emojis)

    def _rivalry_context_for_match(self, match: Match) -> RivalryRatingContext:
        """Return rivalry rating context for a match based on current state."""

        active_pairs = 0
        blowoff_pairs = 0
        has_cooldown = False
        for wrestler_a_id, wrestler_b_id in ordered_pairs(match.wrestler_ids):
            key = normalize_pair(wrestler_a_id, wrestler_b_id)
            if key in self.cooldown_states:
                has_cooldown = True
                continue
            rivalry = self.rivalry_states.get(key)
            if rivalry is None or rivalry.rivalry_value <= 0:
                continue
            if rivalry.rivalry_value >= constants.RIVALRY_LEVEL_CAP:
                blowoff_pairs += 1
            else:
                active_pairs += 1
        return RivalryRatingContext(
            active_pairs=active_pairs,
            blowoff_pairs=blowoff_pairs,
            has_cooldown=has_cooldown,
        )

    def _advance_rivalries(self, show: Show) -> None:
        """Advance rivalry and cooldown state at show end."""

        cooldown_keys = set(self.cooldown_states.keys())
        blowoff_keys: set[PairKey] = set()

        for slot in show.scheduled_slots:
            if not isinstance(slot, Match):
                continue
            for wrestler_a_id, wrestler_b_id in ordered_pairs(slot.wrestler_ids):
                key = normalize_pair(wrestler_a_id, wrestler_b_id)
                if key in cooldown_keys:
                    self.rivalry_states.pop(key, None)
                    continue
                rivalry = self.rivalry_states.get(key)
                current_value = rivalry.rivalry_value if rivalry else 0
                if current_value >= constants.RIVALRY_LEVEL_CAP:
                    blowoff_keys.add(key)
                    continue
                new_value = min(constants.RIVALRY_LEVEL_CAP, current_value + 1)
                self.rivalry_states[key] = RivalryState(
                    wrestler_a_id=key[0],
                    wrestler_b_id=key[1],
                    rivalry_value=new_value,
                )

        if self.cooldown_states:
            updated: Dict[PairKey, CooldownState] = {}
            for key, cooldown in self.cooldown_states.items():
                remaining = cooldown.remaining_shows - 1
                if remaining > 0:
                    updated[key] = CooldownState(
                        wrestler_a_id=key[0],
                        wrestler_b_id=key[1],
                        remaining_shows=remaining,
                    )
            self.cooldown_states = updated

        for key in blowoff_keys:
            self.rivalry_states.pop(key, None)
            self.cooldown_states[key] = CooldownState(
                wrestler_a_id=key[0],
                wrestler_b_id=key[1],
                remaining_shows=constants.COOLDOWN_SHOWS,
            )

    def _rivalry_emoji(self, rivalry_value: int) -> str:
        """Return the emoji for a rivalry value."""

        level = min(constants.RIVALRY_LEVEL_CAP, rivalry_value)
        emojis = {
            1: "⚡",
            2: "🔥",
            3: "⚔️",
            4: "💥",
        }
        return emojis.get(level, "")

    def _cooldown_emoji(self, remaining_shows: int) -> str:
        """Return the emoji for cooldown remaining shows."""

        if remaining_shows >= 5:
            return "🧊"
        if remaining_shows >= 3:
            return "❄️"
        if remaining_shows >= 1:
            return "💧"
        return ""


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
