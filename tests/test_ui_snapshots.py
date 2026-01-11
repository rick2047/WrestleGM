"""UI snapshot tests for canonical screens."""

from __future__ import annotations

from tests.ui_snapshot_utils import assert_svg_snapshot
from tests.ui_test_utils import (
    TestWrestleGMApp,
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


def test_snapshot_s1_main_menu_default(pytestconfig) -> None:
    app = TestWrestleGMApp()
    assert_svg_snapshot(
        name="S1_main_menu_default",
        app=app,
        update_snapshots=pytestconfig.getoption("update_snapshots"),
    )


def test_snapshot_s2_game_hub_default(pytestconfig) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)

    assert_svg_snapshot(
        name="S2_game_hub_default",
        app=app,
        update_snapshots=pytestconfig.getoption("update_snapshots"),
        run_before=run_before,
    )


def test_snapshot_s3_booking_hub_empty(pytestconfig) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        await wait_for_screen(pilot, BookingHubScreen)

    assert_svg_snapshot(
        name="S3_booking_hub_empty",
        app=app,
        update_snapshots=pytestconfig.getoption("update_snapshots"),
        run_before=run_before,
    )


def test_snapshot_s4_booking_hub_filled(pytestconfig) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        seed_show_card(pilot.app.state)
        if isinstance(pilot.app.screen, BookingHubScreen):
            pilot.app.screen.refresh_view()
        await wait_for_screen(pilot, BookingHubScreen)

    assert_svg_snapshot(
        name="S4_booking_hub_filled",
        app=app,
        update_snapshots=pytestconfig.getoption("update_snapshots"),
        run_before=run_before,
    )


def test_snapshot_s5_match_booking_empty(pytestconfig) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        await open_match_booking(pilot, 0)

    assert_svg_snapshot(
        name="S5_match_booking_empty",
        app=app,
        update_snapshots=pytestconfig.getoption("update_snapshots"),
        run_before=run_before,
    )


def test_snapshot_s6_match_booking_filled(pytestconfig) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        seed_show_card(pilot.app.state)
        if isinstance(pilot.app.screen, BookingHubScreen):
            pilot.app.screen.refresh_view()
        await open_match_booking(pilot, 0)

    assert_svg_snapshot(
        name="S6_match_booking_filled",
        app=app,
        update_snapshots=pytestconfig.getoption("update_snapshots"),
        run_before=run_before,
    )


def test_snapshot_s7_wrestler_selection_default(pytestconfig) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        await open_match_booking(pilot, 0)
        await pilot.press("enter")
        await wait_for_screen(pilot, WrestlerSelectionScreen)

    assert_svg_snapshot(
        name="S7_wrestler_selection_default",
        app=app,
        update_snapshots=pytestconfig.getoption("update_snapshots"),
        run_before=run_before,
    )


def test_snapshot_s8_match_type_selection_default(pytestconfig) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        await open_match_booking(pilot, 0)
        await pilot.press("down", "down", "enter")
        await wait_for_screen(pilot, MatchTypeSelectionScreen)

    assert_svg_snapshot(
        name="S8_match_type_selection_default",
        app=app,
        update_snapshots=pytestconfig.getoption("update_snapshots"),
        run_before=run_before,
    )


def test_snapshot_s9_match_booking_confirmation_modal(pytestconfig) -> None:
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

    assert_svg_snapshot(
        name="S9_match_booking_confirmation_modal",
        app=app,
        update_snapshots=pytestconfig.getoption("update_snapshots"),
        run_before=run_before,
    )


def test_snapshot_s10_show_results_default(pytestconfig) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        seed_show_card(pilot.app.state)
        pilot.app.state.run_show()
        pilot.app.switch_screen(ResultsScreen())
        await wait_for_screen(pilot, ResultsScreen)

    assert_svg_snapshot(
        name="S10_show_results_default",
        app=app,
        update_snapshots=pytestconfig.getoption("update_snapshots"),
        run_before=run_before,
    )


def test_snapshot_s11_roster_overview_default(pytestconfig) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_roster(pilot)

    assert_svg_snapshot(
        name="S11_roster_overview_default",
        app=app,
        update_snapshots=pytestconfig.getoption("update_snapshots"),
        run_before=run_before,
    )
