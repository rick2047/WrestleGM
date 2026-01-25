"""Shared formatting helpers for the Textual UI."""

from __future__ import annotations

from wrestlegm import constants
from wrestlegm.models import WrestlerState

FATIGUE_ICON = "🥱"
EMPTY_ICON = "⚠️"
BLOCK_ICON = "⛔"
ALIGNMENT_EMOJI = {"Face": "😃", "Heel": "😈"}


def format_stars(rating: float) -> str:
    """Render a 0.0-5.0 rating as stars with half-star precision."""

    full = int(rating)
    half = 1 if rating - full >= 0.5 else 0
    empty = 5 - full - half
    return "".join(["★"] * full + ["½"] * half + ["☆"] * empty)


def build_name_cell(name: str, alignment: str) -> str:
    """Format the emoji + name cell for roster tables."""

    emoji = ALIGNMENT_EMOJI[alignment]
    trimmed = truncate_name(name)
    return f"{emoji} {trimmed}"


def build_pop_cell(popularity: int, stamina: int, booked_marker: str = "") -> str:
    """Format the popularity cell with status markers."""

    fatigue = f" {FATIGUE_ICON}" if stamina <= constants.STAMINA_MIN_BOOKABLE else ""
    return f"{popularity:>3}{fatigue}{booked_marker}"


def build_match_participants(wrestlers: list[WrestlerState]) -> str:
    """Format a vs-separated list of wrestlers with alignment emoji."""

    return " vs ".join(
        build_name_cell(wrestler.name, wrestler.alignment) for wrestler in wrestlers
    )


def match_category_label(match_category_id: str) -> str:
    """Return the display name for a match category."""

    category = constants.MATCH_CATEGORIES.get(match_category_id)
    return category["name"] if category else "Unknown"


def match_category_size(match_category_id: str) -> int:
    """Return the wrestler count for a match category."""

    category = constants.MATCH_CATEGORIES.get(match_category_id)
    return category["size"] if category else 0


def slot_label(slot_index: int, slot_type: str) -> str:
    """Return the label for a slot index and type."""

    count = sum(
        1
        for index in range(slot_index + 1)
        if constants.SHOW_SLOT_TYPES[index] == slot_type
    )
    return f"{slot_type.title()} {count}"


def row_key_to_id(row_key: object) -> str:
    """Normalize Textual row keys to their underlying string ID."""

    value = getattr(row_key, "key", row_key)
    value = getattr(value, "value", value)
    value = getattr(value, "value", value)
    return str(value)


def truncate_name(name: str, max_len: int = 18) -> str:
    """Return the name trimmed to max_len characters with an ellipsis when needed."""

    if len(name) <= max_len:
        return name
    return f"{name[: max_len - 3]}..."
