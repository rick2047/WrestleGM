"""Session management for save/load orchestration."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from wrestlegm import persistence
from wrestlegm.models import MatchTypeDefinition, WrestlerDefinition
from wrestlegm.state import GameState


class SessionManager:
    """Own save/load flows and slot metadata state."""

    def __init__(
        self,
        wrestlers: Iterable[WrestlerDefinition],
        match_types: Iterable[MatchTypeDefinition],
        *,
        seed: int = 1337,
        save_dir: Path | None = None,
    ) -> None:
        self._wrestler_defs = list(wrestlers)
        self._match_type_defs = list(match_types)
        self._default_seed = seed
        self._save_dir = save_dir
        self.current_slot_index: int | None = None
        self.pending_slot_name: str | None = None

    def list_slots(self) -> list[persistence.SaveSlotInfo]:
        """Return slot metadata for selection screens."""

        return persistence.load_slot_index(self._save_dir)

    def new_game(self, slot_index: int, slot_name: str) -> GameState:
        """Start a new session and assign the active slot."""

        state = GameState(
            self._wrestler_defs,
            self._match_type_defs,
            seed=self._default_seed,
        )
        self.current_slot_index = slot_index
        self.pending_slot_name = slot_name
        return state

    def load_game(self, slot_index: int) -> GameState:
        """Load a saved slot and return a hydrated GameState."""

        slots = persistence.load_slot_index(self._save_dir)
        slot_info = next((slot for slot in slots if slot.slot_index == slot_index), None)
        if slot_info is None or not slot_info.exists:
            raise ValueError("empty_slot")
        try:
            payload = persistence.load_save_payload(slot_index, self._save_dir)
        except FileNotFoundError as exc:
            raise ValueError("missing_save_file") from exc
        version = payload.get("version", 0)
        if version != persistence.SAVE_VERSION:
            raise ValueError("unsupported_save_version")
        state_payload = payload.get("state", {})
        state = GameState(
            self._wrestler_defs,
            self._match_type_defs,
            seed=state_payload.get("rng_seed", self._default_seed),
        )
        persistence.deserialize_game_state(state, state_payload)
        self.current_slot_index = slot_index
        self.pending_slot_name = None
        return state

    def save_current_slot(self, state: GameState) -> None:
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
        persistence.save_game_state(state, self.current_slot_index, slot_name, self._save_dir)
        self.pending_slot_name = None

    def clear_save_slot(self, slot_index: int) -> None:
        """Clear a persisted save slot and its metadata."""

        persistence.clear_save_slot(slot_index, self._save_dir)
