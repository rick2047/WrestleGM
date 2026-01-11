"""Ensure snapshot registry remains fixed."""

from __future__ import annotations

from pathlib import Path

EXPECTED_SNAPSHOTS = {
    "test_snapshot_s1_main_menu_default.raw",
    "test_snapshot_s2_game_hub_default.raw",
    "test_snapshot_s3_booking_hub_empty.raw",
    "test_snapshot_s4_booking_hub_filled.raw",
    "test_snapshot_s5_match_booking_empty.raw",
    "test_snapshot_s6_match_booking_filled.raw",
    "test_snapshot_s7_wrestler_selection_default.raw",
    "test_snapshot_s8_match_type_selection_default.raw",
    "test_snapshot_s9_match_booking_confirmation_modal.raw",
    "test_snapshot_s10_show_results_default.raw",
    "test_snapshot_s11_roster_overview_default.raw",
}


def test_snapshot_registry_is_fixed() -> None:
    snapshot_root = Path("tests") / "snapshots" / "test_ui_snapshots"
    if not snapshot_root.exists():
        raise AssertionError("tests/snapshots is missing; run snapshot update.")

    snapshot_files = {
        path.name
        for path in snapshot_root.rglob("*.raw")
    }
    assert snapshot_files == EXPECTED_SNAPSHOTS
