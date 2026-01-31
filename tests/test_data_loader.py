"""Data loading tests."""

from __future__ import annotations

import json
from pathlib import Path

from wrestlegm.data import load_match_types


def test_match_type_base_cost_defaults_to_zero(tmp_path: Path) -> None:
    payload = [
        {
            "id": "standard",
            "name": "Standard",
            "description": "",
            "modifiers": {
                "outcome_chaos": 0.2,
                "rating_bonus": 0,
                "rating_variance": 6,
                "stamina_cost_winner": 12,
                "stamina_cost_loser": 14,
                "popularity_delta_winner": 2,
                "popularity_delta_loser": -1,
            },
        }
    ]
    path = tmp_path / "match_types.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    match_types = load_match_types(path)
    assert match_types[0].base_cost == 0
