"""Bankruptcy flow tests."""

from __future__ import annotations

from wrestlegm.ui import BankruptcyScreen, GameHubScreen

from tests.ui_test_utils import (
    TestWrestleGMApp,
    VIEWPORT_SIZE,
    assert_screen,
    run_async,
    start_new_game,
    wait_for_screen,
)


def test_bankruptcy_blocks_booking() -> None:
    """Ensure bankruptcy routes to the bankruptcy screen before booking."""

    async def run_flow() -> None:
        app = TestWrestleGMApp()
        async with app.run_test(size=VIEWPORT_SIZE) as pilot:
            await start_new_game(pilot)
            await pilot.press("escape")
            await wait_for_screen(pilot, GameHubScreen)
            app.state.money = 0
            await pilot.press("enter")
            await wait_for_screen(pilot, BankruptcyScreen)
            assert_screen(app, BankruptcyScreen)

    run_async(run_flow())
