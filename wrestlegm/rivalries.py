"""Rivalry and cooldown tracking helpers."""

from __future__ import annotations

from itertools import combinations
from typing import Iterable

from wrestlegm import constants
from wrestlegm.models import (
    CooldownState,
    Match,
    PairKey,
    RivalryState,
    Show,
    normalize_pair,
)
from wrestlegm.sim import RivalryRatingContext


def ordered_pairs(wrestler_ids: Iterable[str]) -> list[tuple[str, str]]:
    """Return ordered unique pairs based on the wrestler list order."""

    ids = list(wrestler_ids)
    return list(combinations(ids, 2))


class RivalryManager:
    """Track rivalry and cooldown state and progression."""

    def __init__(self) -> None:
        self.rivalry_states: dict[PairKey, RivalryState] = {}
        self.cooldown_states: dict[PairKey, CooldownState] = {}

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

    def rivalry_context_for_match(self, match: Match) -> RivalryRatingContext:
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

    def advance(self, show: Show) -> None:
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
            self.cooldown_states = {
                key: CooldownState(
                    wrestler_a_id=key[0],
                    wrestler_b_id=key[1],
                    remaining_shows=cooldown.remaining_shows - 1,
                )
                for key, cooldown in self.cooldown_states.items()
                if cooldown.remaining_shows > 1
            }

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
