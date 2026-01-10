"""Load data-driven definitions from JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from wrestlegm.models import MatchTypeDefinition, MatchTypeModifiers, WrestlerDefinition

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def load_wrestlers(path: Path | None = None) -> List[WrestlerDefinition]:
    """Load wrestler definitions from JSON."""

    file_path = path or DATA_DIR / "wrestlers.json"
    data = json.loads(file_path.read_text(encoding="utf-8"))
    return [WrestlerDefinition(**entry) for entry in data]


def load_match_types(path: Path | None = None) -> List[MatchTypeDefinition]:
    """Load match type definitions from JSON."""

    file_path = path or DATA_DIR / "match_types.json"
    data = json.loads(file_path.read_text(encoding="utf-8"))
    match_types: List[MatchTypeDefinition] = []
    for entry in data:
        modifiers = MatchTypeModifiers(**entry["modifiers"])
        match_types.append(
            MatchTypeDefinition(
                id=entry["id"],
                name=entry["name"],
                description=entry["description"],
                modifiers=modifiers,
            )
        )
    return match_types
