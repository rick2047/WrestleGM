"""UI flow tests driven by Textual's Pilot."""

from __future__ import annotations

from wrestlegm import constants
from wrestlegm.ui import (
    BookingHubScreen,
    GameHubScreen,
    MainMenuScreen,
    MatchBookingScreen,
    NameSaveSlotModal,
    OverwriteSaveSlotModal,
    ResultsScreen,
    RosterScreen,
    SaveSlotSelectionScreen,
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
    seed_show_card,
    select_match_category,
    select_wrestler,
    start_new_game,
    wait_for_condition,
    wait_for_screen,
)


def test_core_flow_new_game_booking_results_roster() -> None:
    """Drive core gameplay flows using keyboard-only input."""

    async def run_flow() -> None:
            app = TestWrestleGMApp()
            async with app.run_test(size=VIEWPORT_SIZE) as pilot:
                assert_screen(app, MainMenuScreen)
                await start_new_game(pilot)
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
                    await select_match_category(pilot, 0)
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


def test_load_game_flow() -> None:
    """Ensure Load Game routes through slot selection to booking hub."""

    async def run_flow() -> None:
        app = TestWrestleGMApp()
        seed_show_card(app.state)
        app.state.run_show()
        app.state.current_slot_index = 1
        app.state.pending_slot_name = "Test"
        app.state.save_current_slot()

        async with app.run_test(size=VIEWPORT_SIZE) as pilot:
            assert_screen(app, MainMenuScreen)
            await pilot.press("down", "enter")
            await wait_for_screen(pilot, SaveSlotSelectionScreen)
            await pilot.press("enter")
            await wait_for_screen(pilot, BookingHubScreen)

    run_async(run_flow())


def test_new_game_overwrite_flow_prefills_name() -> None:
    """Ensure overwriting a slot pre-fills the name modal."""

    async def run_flow() -> None:
        app = TestWrestleGMApp()
        seed_show_card(app.state)
        app.state.run_show()
        app.state.current_slot_index = 1
        app.state.pending_slot_name = "My Save"
        app.state.save_current_slot()

        async with app.run_test(size=VIEWPORT_SIZE) as pilot:
            assert_screen(app, MainMenuScreen)
            await pilot.press("enter")
            await wait_for_screen(pilot, SaveSlotSelectionScreen)
            await pilot.press("enter")
            await wait_for_screen(pilot, OverwriteSaveSlotModal)
            await pilot.press("enter")
            await wait_for_screen(pilot, NameSaveSlotModal)
            modal = app.screen
            assert isinstance(modal, NameSaveSlotModal)
            assert modal.name_input.value == "My Save"
            await pilot.press("enter")
            await wait_for_screen(pilot, BookingHubScreen)

    run_async(run_flow())


def test_name_save_slot_blocks_empty_name() -> None:
    """Ensure the name modal blocks empty input."""

    async def run_flow() -> None:
        app = TestWrestleGMApp()
        async with app.run_test(size=VIEWPORT_SIZE) as pilot:
            await pilot.press("enter")
            await wait_for_screen(pilot, SaveSlotSelectionScreen)
            await pilot.press("enter")
            await wait_for_screen(pilot, NameSaveSlotModal)
            modal = app.screen
            assert isinstance(modal, NameSaveSlotModal)
            assert modal.confirm_button.disabled is True

    run_async(run_flow())


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
            screen.action_focus_next()
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
