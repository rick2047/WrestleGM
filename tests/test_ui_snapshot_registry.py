"""Ensure snapshot registry remains fixed."""

from __future__ import annotations

from pathlib import Path

EXPECTED_SNAPSHOTS = {
    "S1_main_menu_default.svg",
    "S2_game_hub_default.svg",
    "S3_booking_hub_empty.svg",
    "S4_booking_hub_filled.svg",
    "S5_match_booking_empty.svg",
    "S6_match_booking_filled.svg",
    "S7_wrestler_selection_default.svg",
    "S8_match_type_selection_default.svg",
    "S9_match_booking_confirmation_modal.svg",
    "S10_show_results_default.svg",
    "S11_roster_overview_default.svg",
}


def test_snapshot_registry_is_fixed() -> None:
    snapshot_root = Path("tests") / "snapshots"
    if not snapshot_root.exists():
        raise AssertionError("tests/snapshots is missing; run snapshot update.")

    snapshot_files = {
        path.name
        for path in snapshot_root.rglob("*.svg")
        if "__failed__" not in path.parts
    }
    assert snapshot_files == EXPECTED_SNAPSHOTS
