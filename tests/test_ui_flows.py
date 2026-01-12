"""UI flow tests driven by Textual's Pilot."""

from __future__ import annotations

from wrestlegm import constants
from wrestlegm.ui import (
    BookingHubScreen,
    GameHubScreen,
    MainMenuScreen,
    MatchBookingScreen,
    ResultsScreen,
    RosterScreen,
)

from tests.ui_test_utils import (
    TestWrestleGMApp,
    VIEWPORT_SIZE,
    assert_screen,
    confirm_booking,
    open_booking_hub,
    open_match_booking,
    open_promo_booking,
    open_roster,
    run_async,
    select_match_type,
    select_wrestler,
    start_new_game,
    wait_for_screen,
)


def test_core_flow_new_game_booking_results_roster() -> None:
    """Drive core gameplay flows using keyboard-only input."""

    async def run_flow() -> None:
        app = TestWrestleGMApp()
        async with app.run_test(size=VIEWPORT_SIZE) as pilot:
            assert_screen(app, MainMenuScreen)
            await start_new_game(pilot)
            assert_screen(app, GameHubScreen)

            await open_booking_hub(pilot)
            assert_screen(app, BookingHubScreen)
            booking_hub = app.screen
            assert booking_hub.run_button.disabled

            await pilot.press("escape")
            await wait_for_screen(pilot, GameHubScreen)

            await open_roster(pilot)
            assert_screen(app, RosterScreen)
            await pilot.press("escape")
            await wait_for_screen(pilot, GameHubScreen)

            await open_booking_hub(pilot)
            assert_screen(app, BookingHubScreen)

            row_cursor = iter(range(8))
            for slot_index, slot_type in enumerate(constants.SHOW_SLOT_TYPES):
                if slot_type == "match":
                    row_a = next(row_cursor)
                    row_b = next(row_cursor)
                    await open_match_booking(pilot, slot_index)
                    await select_match_type(pilot, 0)
                    await pilot.press("enter")
                    await select_wrestler(pilot, row_a)

                    await pilot.press("down", "enter")
                    await select_wrestler(pilot, row_b)
                    await confirm_booking(pilot)
                else:
                    row = next(row_cursor)
                    await open_promo_booking(pilot, slot_index)
                    await pilot.press("enter")
                    await select_wrestler(pilot, row)
                    await confirm_booking(pilot)

                assert app.state.show_card[slot_index] is not None
                if slot_index < constants.SHOW_SLOT_COUNT - 1:
                    booking_hub = app.screen
                    assert booking_hub.run_button.disabled

            booking_hub = app.screen
            assert not booking_hub.run_button.disabled
            await pilot.press("r")
            await wait_for_screen(pilot, ResultsScreen)

            await pilot.press("enter")
            await wait_for_screen(pilot, GameHubScreen)

    run_async(run_flow())


def test_match_type_change_trims_rows() -> None:
    """Ensure match type changes keep earliest wrestlers and trim extras."""

    async def run_flow() -> None:
        app = TestWrestleGMApp()
        async with app.run_test(size=VIEWPORT_SIZE) as pilot:
            await start_new_game(pilot)
            await open_booking_hub(pilot)
            await open_match_booking(pilot, 0)
            await select_match_type(pilot, 1)

            assert_screen(app, MatchBookingScreen)
            await pilot.press("enter")
            await select_wrestler(pilot, 0)

            await pilot.press("down", "enter")
            await select_wrestler(pilot, 1)

            await pilot.press("down", "enter")
            await select_wrestler(pilot, 2)

            assert_screen(app, MatchBookingScreen)
            screen = app.screen
            assert len(screen.draft.wrestler_ids) == 3

            await pilot.press("down", "enter")
            await select_match_type(pilot, 0)

            assert_screen(app, MatchBookingScreen)
            assert len(screen.draft.wrestler_ids) == 2

    run_async(run_flow())
