"""Persistence tests for save/load behavior."""

from __future__ import annotations

from pathlib import Path
import json

import pytest

from wrestlegm import persistence
from wrestlegm.data import load_match_types, load_wrestlers
from wrestlegm.state import GameState

from tests.ui_test_utils import seed_show_card


def test_save_load_round_trip_integrity(tmp_path: Path) -> None:
    wrestlers = load_wrestlers()
    match_types = load_match_types()
    state = GameState(wrestlers, match_types, save_dir=tmp_path)

    seed_show_card(state)
    state.run_show()
    state.current_slot_index = 1
    state.pending_slot_name = "Test"
    state.save_current_slot()

    loaded = GameState(wrestlers, match_types, save_dir=tmp_path)
    loaded.load_slot(1)

    assert loaded.show_index == state.show_index
    assert loaded.show_card == state.show_card
    assert loaded.rivalry_states == state.rivalry_states
    assert loaded.cooldown_states == state.cooldown_states
    assert loaded.roster.keys() == state.roster.keys()
    for wrestler_id in state.roster:
        assert loaded.roster[wrestler_id] == state.roster[wrestler_id]


def test_rng_determinism_across_save_load(tmp_path: Path) -> None:
    wrestlers = load_wrestlers()
    match_types = load_match_types()
    state = GameState(wrestlers, match_types, save_dir=tmp_path)

    seed_show_card(state)
    state.run_show()
    state.current_slot_index = 1
    state.pending_slot_name = "Test"
    state.save_current_slot()

    loaded = GameState(wrestlers, match_types, save_dir=tmp_path)
    loaded.load_slot(1)

    seed_show_card(state)
    seed_show_card(loaded)
    show_a = state.run_show()
    show_b = loaded.run_show()

    assert len(show_a.results) == len(show_b.results)
    for result_a, result_b in zip(show_a.results, show_b.results):
        assert result_a == result_b
    assert show_a.show_rating == show_b.show_rating


def test_load_rejects_empty_slot(tmp_path: Path) -> None:
    wrestlers = load_wrestlers()
    match_types = load_match_types()
    state = GameState(wrestlers, match_types, save_dir=tmp_path)

    with pytest.raises(ValueError, match="empty_slot"):
        state.load_slot(1)


def test_load_rejects_unsupported_version(tmp_path: Path) -> None:
    wrestlers = load_wrestlers()
    match_types = load_match_types()
    state = GameState(wrestlers, match_types, save_dir=tmp_path)

    persistence.save_slot_index(
        [
            persistence.SaveSlotInfo(
                slot_index=1,
                name="Test",
                exists=True,
                last_saved_show_index=1,
            ),
            persistence.SaveSlotInfo(
                slot_index=2,
                name=None,
                exists=False,
                last_saved_show_index=None,
            ),
            persistence.SaveSlotInfo(
                slot_index=3,
                name=None,
                exists=False,
                last_saved_show_index=None,
            ),
        ],
        tmp_path,
    )
    payload = {
        "version": 1,
        "slot": {"slot_index": 1, "name": "Test"},
        "state": {"show_index": 1, "show_card": [], "rng_seed": 1337},
    }
    persistence.slot_path(1, tmp_path).write_text(
        json.dumps(payload), encoding="utf-8"
    )

    with pytest.raises(ValueError, match="unsupported_save_version"):
        state.load_slot(1)
