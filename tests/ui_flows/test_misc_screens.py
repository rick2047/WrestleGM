"""Navigation coverage for remaining screens and modals."""

from __future__ import annotations

from wrestlegm.ui import (
    ConfirmBookingModal,
    ErrorModal,
    PromoBookingScreen,
    SimulatingScreen,
    WrestlerSelectionScreen,
)

from tests.ui_test_utils import (
    TestWrestleGMApp,
    VIEWPORT_SIZE,
    assert_screen,
    open_booking_hub,
    open_promo_booking,
    run_async,
    seed_show_card,
    select_wrestler,
    start_new_game,
    wait_for_screen,
)


def test_promo_booking_shows_selection_screen() -> None:
    """Ensure promo booking opens wrestler selection."""

    async def run_flow() -> None:
        app = TestWrestleGMApp()
        async with app.run_test(size=VIEWPORT_SIZE) as pilot:
            await start_new_game(pilot)
            await open_booking_hub(pilot)
            await open_promo_booking(pilot, 1)
            assert_screen(app, PromoBookingScreen)
            await pilot.press("enter")
            await wait_for_screen(pilot, WrestlerSelectionScreen)
            await pilot.press("escape")
            await wait_for_screen(pilot, PromoBookingScreen)

    run_async(run_flow())


def test_confirm_modal_and_simulating_screen() -> None:
    """Ensure confirmation modal and simulating screen appear during run show."""

    async def run_flow() -> None:
        app = TestWrestleGMApp()
        async with app.run_test(size=VIEWPORT_SIZE) as pilot:
            await start_new_game(pilot)
            await open_booking_hub(pilot)
            await open_promo_booking(pilot, 1)
            await pilot.press("enter")
            await wait_for_screen(pilot, WrestlerSelectionScreen)
            await select_wrestler(pilot, 0)
            await wait_for_screen(pilot, PromoBookingScreen)
            screen = app.screen
            screen.confirm_button.press()
            await wait_for_screen(pilot, ConfirmBookingModal)
            await pilot.press("escape")
            await wait_for_screen(pilot, PromoBookingScreen)
            await pilot.press("escape")
            await open_booking_hub(pilot)

            seed_show_card(app.state)
            booking_hub = app.screen
            booking_hub.refresh_view()
            await pilot.press("r")
            await wait_for_screen(pilot, SimulatingScreen)

    run_async(run_flow())


def test_load_error_modal() -> None:
    """Ensure load errors surface the error modal screen."""

    async def run_flow() -> None:
        app = TestWrestleGMApp()
        async with app.run_test(size=VIEWPORT_SIZE) as pilot:
            app.load_game(2)
            await wait_for_screen(pilot, ErrorModal)

    run_async(run_flow())
