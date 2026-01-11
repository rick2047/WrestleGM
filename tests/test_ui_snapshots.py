"""UI snapshot tests for canonical screens."""

from __future__ import annotations

from tests.ui_test_utils import (
    TestWrestleGMApp,
    VIEWPORT_SIZE,
    open_booking_hub,
    open_match_booking,
    open_roster,
    seed_show_card,
    select_match_type,
    select_wrestler,
    start_new_game,
    wait_for_screen,
)
from wrestlegm.ui import (
    BookingHubScreen,
    ConfirmBookingModal,
    MatchTypeSelectionScreen,
    ResultsScreen,
    WrestlerSelectionScreen,
)


def test_snapshot_s1_main_menu_default(snap_compare) -> None:
    app = TestWrestleGMApp()
    assert snap_compare(app, terminal_size=VIEWPORT_SIZE)


def test_snapshot_s2_game_hub_default(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s3_booking_hub_empty(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        await wait_for_screen(pilot, BookingHubScreen)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s4_booking_hub_filled(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        seed_show_card(pilot.app.state)
        if isinstance(pilot.app.screen, BookingHubScreen):
            pilot.app.screen.refresh_view()
        await wait_for_screen(pilot, BookingHubScreen)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s5_match_booking_empty(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        await open_match_booking(pilot, 0)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s6_match_booking_filled(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        seed_show_card(pilot.app.state)
        if isinstance(pilot.app.screen, BookingHubScreen):
            pilot.app.screen.refresh_view()
        await open_match_booking(pilot, 0)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s7_wrestler_selection_default(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        await open_match_booking(pilot, 0)
        await pilot.press("enter")
        await wait_for_screen(pilot, WrestlerSelectionScreen)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s8_match_type_selection_default(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        await open_match_booking(pilot, 0)
        await pilot.press("down", "down", "enter")
        await wait_for_screen(pilot, MatchTypeSelectionScreen)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s9_match_booking_confirmation_modal(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        await open_match_booking(pilot, 0)
        await pilot.press("enter")
        await select_wrestler(pilot, 0)

        await pilot.press("down", "enter")
        await select_wrestler(pilot, 1)

        await pilot.press("down", "enter")
        await select_match_type(pilot, 0)

        await pilot.press("down", "enter")
        await wait_for_screen(pilot, ConfirmBookingModal)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s10_show_results_default(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        seed_show_card(pilot.app.state)
        pilot.app.state.run_show()
        pilot.app.switch_screen(ResultsScreen())
        await wait_for_screen(pilot, ResultsScreen)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s11_roster_overview_default(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_roster(pilot)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)
