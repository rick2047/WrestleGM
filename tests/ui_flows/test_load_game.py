"""Load game and error modal flows."""

from __future__ import annotations

from wrestlegm.ui import (
    GameHubScreen,
    MainMenuScreen,
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


def test_load_game_flow() -> None:
    """Ensure Load Game routes through slot selection to game hub."""

    async def run_flow() -> None:
        app = TestWrestleGMApp()
        seed_show_card(app.state)
        app.state.run_show()
        app.session.current_slot_index = 1
        app.session.pending_slot_name = "Test"
        app.session.save_current_slot(app.state)

        async with app.run_test(size=VIEWPORT_SIZE) as pilot:
            assert_screen(app, MainMenuScreen)
            await pilot.press("down", "enter")
            await wait_for_screen(pilot, SaveSlotSelectionScreen)
            await pilot.press("enter")
            await wait_for_screen(pilot, GameHubScreen)

    run_async(run_flow())
