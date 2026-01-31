"""Draft state containers for booking flows."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BookingDraft:
    """Track in-progress booking choices before committing to GameState.

    Responsibilities:
    - Store selected wrestler and match type ids for a single slot.
    - Provide a completeness check used by UI validation.
    """

    wrestler_ids: list[Optional[str]] = field(default_factory=list)
    match_category_id: Optional[int] = None
    match_type_id: Optional[str] = None

    def is_complete(self, required_count: int) -> bool:
        """Return True when all booking fields are set."""

        if self.match_category_id is None or not self.match_type_id:
            return False
        if len(self.wrestler_ids) != required_count:
            return False
        return all(self.wrestler_ids)

    def ensure_size(self, required_count: int) -> None:
        """Resize wrestler slots to match the required count."""

        if required_count < 0:
            return
        if len(self.wrestler_ids) > required_count:
            self.wrestler_ids = self.wrestler_ids[:required_count]
        elif len(self.wrestler_ids) < required_count:
            self.wrestler_ids.extend([None] * (required_count - len(self.wrestler_ids)))


@dataclass
class PromoDraft:
    """Track in-progress promo booking choices before committing."""

    wrestler_id: Optional[str] = None

    def is_complete(self) -> bool:
        """Return True when the promo wrestler is set."""

        return bool(self.wrestler_id)
