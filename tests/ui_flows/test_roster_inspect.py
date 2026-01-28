"""Roster inspection flow tests."""

from __future__ import annotations

from wrestlegm.ui import BookingHubScreen, GameHubScreen, MainMenuScreen, RosterScreen
from wrestlegm.ui.screens.wrestler_selection import WrestlerInspectModal

from tests.ui_test_utils import (
    TestWrestleGMApp,
    VIEWPORT_SIZE,
    assert_screen,
    open_roster,
    run_async,
    start_new_game,
    wait_for_screen,
)


def test_roster_inspect_modal_opens_and_restores_focus() -> None:
    """Ensure roster inspect opens a modal and restores focus on close."""

    async def run_flow() -> None:
        app = TestWrestleGMApp()
        async with app.run_test(size=VIEWPORT_SIZE) as pilot:
            assert_screen(app, MainMenuScreen)
            await start_new_game(pilot)
            await wait_for_screen(pilot, BookingHubScreen)
            await pilot.press("escape")
            await wait_for_screen(pilot, GameHubScreen)
            await open_roster(pilot)
            assert_screen(app, RosterScreen)

            await pilot.press("i")
            await wait_for_screen(pilot, WrestlerInspectModal)
            await pilot.press("escape")
            await wait_for_screen(pilot, RosterScreen)

            screen = app.screen
            assert isinstance(screen, RosterScreen)
            assert app.focused is screen.table

    run_async(run_flow())
