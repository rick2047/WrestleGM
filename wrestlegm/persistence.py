"""Persistence helpers for save/load state."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Iterable, TYPE_CHECKING

from wrestlegm.models import (
    CooldownState,
    Match,
    Promo,
    RivalryState,
    WrestlerState,
    normalize_pair,
)

if TYPE_CHECKING:
    from wrestlegm.state import GameState

SAVE_VERSION = 1
SLOT_COUNT = 3
SLOT_INDEX_NAME = "slots.json"
DEFAULT_SAVE_DIR = Path("dist/data/save")


@dataclass
class SaveSlotInfo:
    """Metadata for save slot selection."""

    slot_index: int
    name: str | None
    exists: bool
    last_saved_show_index: int | None


def ensure_save_dir(base_dir: Path | None = None) -> Path:
    """Ensure the save directory exists and return it."""

    save_dir = base_dir or DEFAULT_SAVE_DIR
    save_dir.mkdir(parents=True, exist_ok=True)
    return save_dir


def slot_path(slot_index: int, base_dir: Path | None = None) -> Path:
    """Return the save file path for a slot."""

    return ensure_save_dir(base_dir) / f"slot_{slot_index}.json"


def slot_index_path(base_dir: Path | None = None) -> Path:
    """Return the slot index metadata file path."""

    return ensure_save_dir(base_dir) / SLOT_INDEX_NAME


def default_slots() -> list[SaveSlotInfo]:
    """Return default empty slots for the MVP."""

    return [
        SaveSlotInfo(
            slot_index=slot_index,
            name=None,
            exists=False,
            last_saved_show_index=None,
        )
        for slot_index in range(1, SLOT_COUNT + 1)
    ]


def load_slot_index(base_dir: Path | None = None) -> list[SaveSlotInfo]:
    """Load slot metadata from the index file."""

    path = slot_index_path(base_dir)
    if not path.exists():
        return default_slots()

    data = json.loads(path.read_text(encoding="utf-8"))
    slots_data = data.get("slots", []) if isinstance(data, dict) else []
    slots_by_index: dict[int, SaveSlotInfo] = {
        slot.slot_index: slot for slot in default_slots()
    }
    for entry in slots_data:
        if not isinstance(entry, dict):
            continue
        slot_index = entry.get("slot_index")
        if not isinstance(slot_index, int) or slot_index not in slots_by_index:
            continue
        name = entry.get("name")
        if name is not None and not isinstance(name, str):
            name = None
        exists = bool(entry.get("exists"))
        last_saved_show_index = entry.get("last_saved_show_index")
        if not isinstance(last_saved_show_index, int):
            last_saved_show_index = None
        slots_by_index[slot_index] = SaveSlotInfo(
            slot_index=slot_index,
            name=name,
            exists=exists,
            last_saved_show_index=last_saved_show_index,
        )
    return [slots_by_index[index] for index in range(1, SLOT_COUNT + 1)]


def save_slot_index(slots: Iterable[SaveSlotInfo], base_dir: Path | None = None) -> None:
    """Persist slot metadata for selection screens."""

    payload = {
        "slots": [
            {
                "slot_index": slot.slot_index,
                "name": slot.name,
                "exists": slot.exists,
                "last_saved_show_index": slot.last_saved_show_index,
            }
            for slot in slots
        ]
    }
    path = slot_index_path(base_dir)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def serialize_game_state(state: GameState) -> dict[str, Any]:
    """Serialize GameState into JSON-friendly data."""

    return {
        "roster": [
            {
                "id": wrestler.id,
                "name": wrestler.name,
                "alignment": wrestler.alignment,
                "popularity": wrestler.popularity,
                "stamina": wrestler.stamina,
                "mic_skill": wrestler.mic_skill,
            }
            for wrestler in state.roster.values()
        ],
        "rivalry_states": [
            {
                "wrestler_a_id": rivalry.wrestler_a_id,
                "wrestler_b_id": rivalry.wrestler_b_id,
                "rivalry_value": rivalry.rivalry_value,
            }
            for rivalry in state.rivalry_states.values()
        ],
        "cooldown_states": [
            {
                "wrestler_a_id": cooldown.wrestler_a_id,
                "wrestler_b_id": cooldown.wrestler_b_id,
                "remaining_shows": cooldown.remaining_shows,
            }
            for cooldown in state.cooldown_states.values()
        ],
        "show_index": state.show_index,
        "show_card": [_serialize_slot(slot) for slot in state.show_card],
        "rng_seed": state.engine.seed,
        "rng_state": _to_jsonable(state.engine.rng.getstate()),
    }


def deserialize_game_state(state: GameState, payload: dict[str, Any]) -> None:
    """Apply serialized state data to an existing GameState."""

    roster = {}
    for wrestler_data in payload.get("roster", []):
        roster[wrestler_data["id"]] = WrestlerState(
            id=wrestler_data["id"],
            name=wrestler_data["name"],
            alignment=wrestler_data["alignment"],
            popularity=wrestler_data["popularity"],
            stamina=wrestler_data["stamina"],
            mic_skill=wrestler_data["mic_skill"],
        )
    state.roster = roster

    rivalry_states = {}
    for rivalry_data in payload.get("rivalry_states", []):
        rivalry = RivalryState(
            wrestler_a_id=rivalry_data["wrestler_a_id"],
            wrestler_b_id=rivalry_data["wrestler_b_id"],
            rivalry_value=rivalry_data["rivalry_value"],
        )
        rivalry_states[normalize_pair(rivalry.wrestler_a_id, rivalry.wrestler_b_id)] = rivalry
    state.rivalry_states = rivalry_states

    cooldown_states = {}
    for cooldown_data in payload.get("cooldown_states", []):
        cooldown = CooldownState(
            wrestler_a_id=cooldown_data["wrestler_a_id"],
            wrestler_b_id=cooldown_data["wrestler_b_id"],
            remaining_shows=cooldown_data["remaining_shows"],
        )
        cooldown_states[normalize_pair(cooldown.wrestler_a_id, cooldown.wrestler_b_id)] = cooldown
    state.cooldown_states = cooldown_states

    state.show_index = payload.get("show_index", 1)
    show_card_data = payload.get("show_card", [])
    show_card = [_deserialize_slot(slot_data) for slot_data in show_card_data]
    if len(show_card) < len(state.show_card):
        show_card.extend([None] * (len(state.show_card) - len(show_card)))
    state.show_card = show_card[: len(state.show_card)]
    state.last_show = None

    rng_seed = payload.get("rng_seed", state.engine.seed)
    rng_state = payload.get("rng_state")
    state.engine.seed = rng_seed
    if rng_state is not None:
        state.engine.rng.setstate(_to_tuple(rng_state))


def load_save_payload(slot_index: int, base_dir: Path | None = None) -> dict[str, Any]:
    """Load a save payload from disk."""

    path = slot_path(slot_index, base_dir)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("corrupt_save_file") from exc


def save_payload(
    state: GameState,
    slot_index: int,
    slot_name: str,
) -> dict[str, Any]:
    """Create the save payload for the current state."""

    return {
        "version": SAVE_VERSION,
        "slot": {
            "slot_index": slot_index,
            "name": slot_name,
        },
        "state": serialize_game_state(state),
    }


def save_game_state(
    state: GameState,
    slot_index: int,
    slot_name: str,
    base_dir: Path | None = None,
) -> None:
    """Persist a save file and update the slot index metadata."""

    payload = save_payload(state, slot_index, slot_name)
    path = slot_path(slot_index, base_dir)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    slots = load_slot_index(base_dir)
    last_saved_show_index = max(state.show_index - 1, 0)
    updated_slots = [
        SaveSlotInfo(
            slot_index=slot_index,
            name=slot_name,
            exists=True,
            last_saved_show_index=last_saved_show_index,
        )
        if slot.slot_index == slot_index
        else slot
        for slot in slots
    ]
    save_slot_index(updated_slots, base_dir)


def clear_save_slot(slot_index: int, base_dir: Path | None = None) -> None:
    """Clear a save slot file and metadata."""

    path = slot_path(slot_index, base_dir)
    if path.exists():
        path.unlink()
    slots = load_slot_index(base_dir)
    updated_slots = [
        SaveSlotInfo(
            slot_index=slot_index,
            name=None,
            exists=False,
            last_saved_show_index=None,
        )
        if slot.slot_index == slot_index
        else slot
        for slot in slots
    ]
    save_slot_index(updated_slots, base_dir)


def _serialize_slot(slot: Match | Promo | None) -> dict[str, Any] | None:
    """Serialize a show slot for persistence."""

    if slot is None:
        return None
    if isinstance(slot, Match):
        return {
            "type": "match",
            "wrestler_ids": slot.wrestler_ids,
            "match_category_id": slot.match_category_id,
            "match_type_id": slot.match_type_id,
        }
    return {
        "type": "promo",
        "wrestler_id": slot.wrestler_id,
    }


def _deserialize_slot(data: dict[str, Any] | None) -> Match | Promo | None:
    """Deserialize a show slot from persistence data."""

    if data is None:
        return None
    if data.get("type") == "match":
        return Match(
            wrestler_ids=list(data.get("wrestler_ids", [])),
            match_category_id=data.get("match_category_id", ""),
            match_type_id=data.get("match_type_id", ""),
        )
    return Promo(wrestler_id=data.get("wrestler_id", ""))


def _to_jsonable(value: Any) -> Any:
    """Convert tuples to lists for JSON serialization."""

    if isinstance(value, tuple):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    return value


def _to_tuple(value: Any) -> Any:
    """Convert lists back into tuples for RNG state restore."""

    if isinstance(value, list):
        return tuple(_to_tuple(item) for item in value)
    return value

