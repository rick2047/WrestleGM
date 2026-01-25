"""Match booking related flows."""

from __future__ import annotations

from wrestlegm.ui import MatchBookingScreen

from tests.ui_test_utils import (
    TestWrestleGMApp,
    VIEWPORT_SIZE,
    assert_screen,
    confirm_booking,
    open_booking_hub,
    open_match_booking,
    run_async,
    select_match_category,
    select_wrestler,
    start_new_game,
    wait_for_condition,
)


def test_match_category_change_trims_rows() -> None:
    """Ensure match category changes keep earliest wrestlers and trim extras."""

    async def run_flow() -> None:
        app = TestWrestleGMApp()
        async with app.run_test(size=VIEWPORT_SIZE) as pilot:
            await start_new_game(pilot)
            await open_booking_hub(pilot)
            await open_match_booking(pilot, 0)
            await select_match_category(pilot, 1)

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

            await confirm_booking(pilot)
            await open_match_booking(pilot, 0)
            await select_match_category(pilot, 0)

            assert_screen(app, MatchBookingScreen)
            screen = app.screen
            assert len(screen.draft.wrestler_ids) == 2

    run_async(run_flow())


def test_match_booking_dropdowns_resize_list_and_change_stipulation() -> None:
    """Ensure wrestler count dropdown resizes the list and stipulation changes."""

    async def run_flow() -> None:
        app = TestWrestleGMApp()
        async with app.run_test(size=VIEWPORT_SIZE) as pilot:
            await start_new_game(pilot)
            await open_booking_hub(pilot)
            await open_match_booking(pilot, 0)

            assert_screen(app, MatchBookingScreen)
            screen = app.screen

            await select_match_category(pilot, 1)
            required_count = screen.required_wrestler_count()
            visible = sum(
                1
                for item in screen.wrestler_list_items
                if item.styles.display != "none"
            )
            assert visible == required_count

            await select_match_category(pilot, 0)
            required_count = screen.required_wrestler_count()
            visible = sum(
                1
                for item in screen.wrestler_list_items
                if item.styles.display != "none"
            )
            assert visible == required_count

            screen.match_type_select.focus()
            await pilot.pause(0.05)
            await pilot.press("enter")
            initial_value = screen.match_type_select.value
            await pilot.press("down")
            await pilot.press("enter")
            await pilot.pause(0.05)
            assert screen.match_type_select.value != initial_value

    run_async(run_flow())


def test_stipulation_dropdown_opens_on_enter() -> None:
    """Ensure Enter opens the stipulation dropdown without errors."""

    async def run_flow() -> None:
        app = TestWrestleGMApp()
        async with app.run_test(size=VIEWPORT_SIZE) as pilot:
            await start_new_game(pilot)
            await open_booking_hub(pilot)
            await open_match_booking(pilot, 0)
            await select_match_category(pilot, 0)

            assert_screen(app, MatchBookingScreen)
            screen = app.screen
            await wait_for_condition(pilot, lambda: hasattr(screen, "fields"))
            screen.match_type_select.focus()
            await pilot.pause(0.05)
            await pilot.press("enter")

            screen = app.screen
            assert screen.match_type_select.expanded is True
            initial_value = screen.match_type_select.value
            await pilot.press("down")
            await pilot.press("enter")
            await pilot.pause(0.05)

            screen = app.screen
            assert screen.match_type_select.expanded is False
            assert screen.match_type_select.value != initial_value

    run_async(run_flow())
