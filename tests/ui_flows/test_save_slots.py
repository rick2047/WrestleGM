"""Save slot and naming modal flows."""

from __future__ import annotations

from wrestlegm.ui import (
    BookingHubScreen,
    MainMenuScreen,
    NameSaveSlotModal,
    OverwriteSaveSlotModal,
    SaveSlotSelectionScreen,
)

from tests.ui_test_utils import (
    TestWrestleGMApp,
    VIEWPORT_SIZE,
    assert_screen,
    run_async,
    seed_show_card,
    wait_for_screen,
)


def test_new_game_overwrite_flow_prefills_name() -> None:
    """Ensure overwriting a slot pre-fills the name modal."""

    async def run_flow() -> None:
        app = TestWrestleGMApp()
        seed_show_card(app.state)
        app.state.run_show()
        app.session.current_slot_index = 1
        app.session.pending_slot_name = "My Save"
        app.session.save_current_slot(app.state)

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
            modal.confirm_button.press()
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
