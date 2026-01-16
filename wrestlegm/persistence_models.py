"""Dataclass snapshots for persistence payloads."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

from wrestlegm.models import (
    Alignment,
    CooldownState,
    Match,
    Promo,
    RivalryState,
    WrestlerState,
    normalize_pair,
)

if TYPE_CHECKING:
    from wrestlegm.state import GameState


@dataclass
class WrestlerSnapshot:
    """Serializable snapshot of wrestler state."""

    id: str
    name: str
    alignment: Alignment
    popularity: int
    stamina: int
    mic_skill: int

    @classmethod
    def from_state(cls, wrestler: WrestlerState) -> "WrestlerSnapshot":
        return cls(
            id=wrestler.id,
            name=wrestler.name,
            alignment=wrestler.alignment,
            popularity=wrestler.popularity,
            stamina=wrestler.stamina,
            mic_skill=wrestler.mic_skill,
        )

    def to_state(self) -> WrestlerState:
        return WrestlerState(
            id=self.id,
            name=self.name,
            alignment=self.alignment,
            popularity=self.popularity,
            stamina=self.stamina,
            mic_skill=self.mic_skill,
        )


@dataclass
class RivalrySnapshot:
    """Serializable snapshot of rivalry state."""

    wrestler_a_id: str
    wrestler_b_id: str
    rivalry_value: int

    @classmethod
    def from_state(cls, rivalry: RivalryState) -> "RivalrySnapshot":
        return cls(
            wrestler_a_id=rivalry.wrestler_a_id,
            wrestler_b_id=rivalry.wrestler_b_id,
            rivalry_value=rivalry.rivalry_value,
        )

    def to_state(self) -> RivalryState:
        return RivalryState(
            wrestler_a_id=self.wrestler_a_id,
            wrestler_b_id=self.wrestler_b_id,
            rivalry_value=self.rivalry_value,
        )


@dataclass
class CooldownSnapshot:
    """Serializable snapshot of cooldown state."""

    wrestler_a_id: str
    wrestler_b_id: str
    remaining_shows: int

    @classmethod
    def from_state(cls, cooldown: CooldownState) -> "CooldownSnapshot":
        return cls(
            wrestler_a_id=cooldown.wrestler_a_id,
            wrestler_b_id=cooldown.wrestler_b_id,
            remaining_shows=cooldown.remaining_shows,
        )

    def to_state(self) -> CooldownState:
        return CooldownState(
            wrestler_a_id=self.wrestler_a_id,
            wrestler_b_id=self.wrestler_b_id,
            remaining_shows=self.remaining_shows,
        )


@dataclass
class MatchSlotSnapshot:
    """Serializable snapshot of a match slot."""

    type: str
    wrestler_ids: list[str]
    match_category_id: str
    match_type_id: str


@dataclass
class PromoSlotSnapshot:
    """Serializable snapshot of a promo slot."""

    type: str
    wrestler_id: str


ShowSlotSnapshot = MatchSlotSnapshot | PromoSlotSnapshot


@dataclass
class GameStateSnapshot:
    """Serializable snapshot of the game state."""

    roster: list[WrestlerSnapshot]
    rivalry_states: list[RivalrySnapshot]
    cooldown_states: list[CooldownSnapshot]
    show_index: int
    show_card: list[ShowSlotSnapshot | None]
    rng_seed: int | None
    rng_state: Any | None

    @classmethod
    def from_game_state(cls, state: "GameState") -> "GameStateSnapshot":
        return cls(
            roster=[WrestlerSnapshot.from_state(wrestler) for wrestler in state.roster.values()],
            rivalry_states=[
                RivalrySnapshot.from_state(rivalry)
                for rivalry in state.rivalry_states.values()
            ],
            cooldown_states=[
                CooldownSnapshot.from_state(cooldown)
                for cooldown in state.cooldown_states.values()
            ],
            show_index=state.show_index,
            show_card=[_slot_snapshot_from_slot(slot) for slot in state.show_card],
            rng_seed=state.engine.seed,
            rng_state=_to_jsonable(state.engine.rng.getstate()),
        )

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "GameStateSnapshot":
        roster_data = payload.get("roster", [])
        if not isinstance(roster_data, list):
            roster_data = []
        roster = [
            WrestlerSnapshot(
                id=entry["id"],
                name=entry["name"],
                alignment=entry["alignment"],
                popularity=entry["popularity"],
                stamina=entry["stamina"],
                mic_skill=entry["mic_skill"],
            )
            for entry in roster_data
        ]
        rivalry_data = payload.get("rivalry_states", [])
        if not isinstance(rivalry_data, list):
            rivalry_data = []
        rivalry_states = [
            RivalrySnapshot(
                wrestler_a_id=entry["wrestler_a_id"],
                wrestler_b_id=entry["wrestler_b_id"],
                rivalry_value=entry["rivalry_value"],
            )
            for entry in rivalry_data
        ]
        cooldown_data = payload.get("cooldown_states", [])
        if not isinstance(cooldown_data, list):
            cooldown_data = []
        cooldown_states = [
            CooldownSnapshot(
                wrestler_a_id=entry["wrestler_a_id"],
                wrestler_b_id=entry["wrestler_b_id"],
                remaining_shows=entry["remaining_shows"],
            )
            for entry in cooldown_data
        ]
        show_card_data = payload.get("show_card", [])
        if not isinstance(show_card_data, list):
            show_card_data = []
        show_card = [_slot_snapshot_from_payload(slot) for slot in show_card_data]
        rng_seed = payload.get("rng_seed")
        if not isinstance(rng_seed, int):
            rng_seed = None
        rng_state = payload.get("rng_state")
        show_index = payload.get("show_index", 1)
        if not isinstance(show_index, int):
            show_index = 1
        return cls(
            roster=roster,
            rivalry_states=rivalry_states,
            cooldown_states=cooldown_states,
            show_index=show_index,
            show_card=show_card,
            rng_seed=rng_seed,
            rng_state=rng_state,
        )

    def apply_to_state(self, state: "GameState") -> None:
        state.roster = {wrestler.id: wrestler.to_state() for wrestler in self.roster}

        rivalry_states: dict[tuple[str, str], RivalryState] = {}
        for rivalry in self.rivalry_states:
            rivalry_state = rivalry.to_state()
            rivalry_states[
                normalize_pair(rivalry_state.wrestler_a_id, rivalry_state.wrestler_b_id)
            ] = rivalry_state
        state.rivalry_states = rivalry_states

        cooldown_states: dict[tuple[str, str], CooldownState] = {}
        for cooldown in self.cooldown_states:
            cooldown_state = cooldown.to_state()
            cooldown_states[
                normalize_pair(cooldown_state.wrestler_a_id, cooldown_state.wrestler_b_id)
            ] = cooldown_state
        state.cooldown_states = cooldown_states

        state.show_index = self.show_index
        show_card = [
            _slot_from_snapshot(slot) if slot is not None else None
            for slot in self.show_card
        ]
        if len(show_card) < len(state.show_card):
            show_card.extend([None] * (len(state.show_card) - len(show_card)))
        state.show_card = show_card[: len(state.show_card)]
        state.last_show = None

        if self.rng_seed is not None:
            state.engine.seed = self.rng_seed
        if self.rng_state is not None:
            state.engine.rng.setstate(_to_tuple(self.rng_state))


@dataclass
class SaveSlotSnapshot:
    """Serializable snapshot of save slot metadata."""

    slot_index: int
    name: str


@dataclass
class SavePayloadSnapshot:
    """Serializable snapshot of the full save payload."""

    version: int
    slot: SaveSlotSnapshot
    state: GameStateSnapshot


def _slot_snapshot_from_slot(slot: Match | Promo | None) -> ShowSlotSnapshot | None:
    if slot is None:
        return None
    if isinstance(slot, Match):
        return MatchSlotSnapshot(
            type="match",
            wrestler_ids=list(slot.wrestler_ids),
            match_category_id=slot.match_category_id,
            match_type_id=slot.match_type_id,
        )
    return PromoSlotSnapshot(
        type="promo",
        wrestler_id=slot.wrestler_id,
    )


def _slot_snapshot_from_payload(data: dict[str, Any] | None) -> ShowSlotSnapshot | None:
    if data is None:
        return None
    if data.get("type") == "match":
        return MatchSlotSnapshot(
            type="match",
            wrestler_ids=list(data.get("wrestler_ids", [])),
            match_category_id=data.get("match_category_id", ""),
            match_type_id=data.get("match_type_id", ""),
        )
    return PromoSlotSnapshot(
        type="promo",
        wrestler_id=data.get("wrestler_id", ""),
    )


def _slot_from_snapshot(slot: ShowSlotSnapshot) -> Match | Promo:
    if slot.type == "match":
        return Match(
            wrestler_ids=list(slot.wrestler_ids),
            match_category_id=slot.match_category_id,
            match_type_id=slot.match_type_id,
        )
    return Promo(wrestler_id=slot.wrestler_id)


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    return value


def _to_tuple(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(_to_tuple(item) for item in value)
    return value
