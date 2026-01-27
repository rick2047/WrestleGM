"""UI snapshot tests for canonical screens."""

from __future__ import annotations

from tests.ui_test_utils import (
    TestWrestleGMApp,
    VIEWPORT_SIZE,
    open_booking_hub,
    open_match_booking,
    open_promo_booking,
    open_roster,
    seed_show_card,
    select_wrestler,
    start_new_game,
    wait_for_screen,
)
from wrestlegm import constants
from wrestlegm.models import CooldownState, RivalryState, normalize_pair
from wrestlegm.ui import (
    BookingHubScreen,
    ConfirmBookingModal,
    GameHubScreen,
    NameSaveSlotModal,
    OverwriteSaveSlotModal,
    PromoBookingScreen,
    ResultsScreen,
    RosterScreen,
    SaveSlotSelectionScreen,
    WrestlerSelectionScreen,
)
from wrestlegm.ui.screens.wrestler_selection import WrestlerInspectModal


def test_snapshot_s1_main_menu_default(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await pilot.pause(0.1)
        await pilot.wait_for_scheduled_animations()
        await pilot.pause(0.1)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s2_game_hub_default(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await pilot.press("escape")
        await wait_for_screen(pilot, GameHubScreen)
        await pilot.pause(0.1)
        await pilot.wait_for_scheduled_animations()
        await pilot.pause(0.1)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s3_booking_hub_empty(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        await wait_for_screen(pilot, BookingHubScreen)
        await pilot.pause(0.1)
        await pilot.wait_for_scheduled_animations()
        await pilot.pause(0.1)

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
        await pilot.pause(0.1)
        await pilot.wait_for_scheduled_animations()
        await pilot.pause(0.1)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s5_match_booking_empty(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        await open_match_booking(pilot, 0)
        await pilot.pause(0.1)
        await pilot.wait_for_scheduled_animations()
        await pilot.pause(0.1)

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
        await pilot.pause(0.1)
        await pilot.wait_for_scheduled_animations()
        await pilot.pause(0.1)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s7_promo_booking_empty(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        await open_promo_booking(pilot, 1)
        await wait_for_screen(pilot, PromoBookingScreen)
        await pilot.pause(0.1)
        await pilot.wait_for_scheduled_animations()
        await pilot.pause(0.1)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s8_promo_booking_filled(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        await open_promo_booking(pilot, 1)
        await pilot.press("enter")
        await select_wrestler(pilot, 0)
        await wait_for_screen(pilot, PromoBookingScreen)
        await pilot.pause(0.1)
        await pilot.wait_for_scheduled_animations()
        await pilot.pause(0.1)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s9_wrestler_selection_default(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        await open_match_booking(pilot, 0)
        await pilot.press("enter")
        await wait_for_screen(pilot, WrestlerSelectionScreen)
        await pilot.pause(0.1)
        await pilot.wait_for_scheduled_animations()
        await pilot.pause(0.1)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s10_wrestler_selection_inspect_modal(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        await open_match_booking(pilot, 0)
        await pilot.press("enter")
        await wait_for_screen(pilot, WrestlerSelectionScreen)
        await pilot.press("down")
        await pilot.press("i")
        await wait_for_screen(pilot, WrestlerInspectModal)
        await pilot.pause(0.1)
        await pilot.wait_for_scheduled_animations()
        await pilot.pause(0.1)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s11_match_booking_confirmation_modal(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        await open_match_booking(pilot, 0)
        await pilot.press("enter")
        await select_wrestler(pilot, 0)
        await pilot.press("down", "enter")
        await select_wrestler(pilot, 1)

        screen = pilot.app.screen
        if isinstance(screen, BookingHubScreen):
            raise AssertionError("Expected MatchBookingScreen")
        screen.confirm_button.press()
        await wait_for_screen(pilot, ConfirmBookingModal)
        modal = pilot.app.screen
        if isinstance(modal, ConfirmBookingModal):
            modal.confirm_button.focus()
            await pilot.pause(0.05)
        await pilot.pause(0.1)
        await pilot.wait_for_scheduled_animations()
        await pilot.pause(0.1)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s12_show_results_default(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        seed_show_card(pilot.app.state)
        pilot.app.state.run_show()
        pilot.app.switch_screen(ResultsScreen())
        await wait_for_screen(pilot, ResultsScreen)
        await pilot.pause(0.1)
        await pilot.wait_for_scheduled_animations()
        await pilot.pause(0.1)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s13_roster_overview_default(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await pilot.press("escape")
        await wait_for_screen(pilot, GameHubScreen)
        await open_roster(pilot)
        await wait_for_screen(pilot, RosterScreen)
        await pilot.pause(0.1)
        await pilot.wait_for_scheduled_animations()
        await pilot.pause(0.1)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s14_booking_hub_rivalry_emojis(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        seed_show_card(pilot.app.state)
        key = normalize_pair("alpha", "bravo")
        pilot.app.state.rivalry_manager.rivalry_states[key] = RivalryState(
            wrestler_a_id=key[0],
            wrestler_b_id=key[1],
            rivalry_value=2,
        )
        if isinstance(pilot.app.screen, BookingHubScreen):
            pilot.app.screen.refresh_view()
        await wait_for_screen(pilot, BookingHubScreen)
        await pilot.pause(0.1)
        await pilot.wait_for_scheduled_animations()
        await pilot.pause(0.1)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s15_booking_hub_cooldown_emojis(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        seed_show_card(pilot.app.state)
        key = normalize_pair("alpha", "bravo")
        pilot.app.state.rivalry_manager.cooldown_states[key] = CooldownState(
            wrestler_a_id=key[0],
            wrestler_b_id=key[1],
            remaining_shows=constants.COOLDOWN_SHOWS,
        )
        if isinstance(pilot.app.screen, BookingHubScreen):
            pilot.app.screen.refresh_view()
        await wait_for_screen(pilot, BookingHubScreen)
        await pilot.pause(0.1)
        await pilot.wait_for_scheduled_animations()
        await pilot.pause(0.1)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s16_match_booking_rivalry_summary(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        key = normalize_pair("alpha", "bravo")
        pilot.app.state.rivalry_manager.rivalry_states[key] = RivalryState(
            wrestler_a_id=key[0],
            wrestler_b_id=key[1],
            rivalry_value=2,
        )
        await open_booking_hub(pilot)
        await open_match_booking(pilot, 0)
        await pilot.press("enter")
        await select_wrestler(pilot, 0)
        await pilot.press("down", "enter")
        await select_wrestler(pilot, 1)
        await pilot.pause(0.1)
        await pilot.wait_for_scheduled_animations()
        await pilot.pause(0.1)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s17_guard_screen(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await pilot.pause(0.1)
        await pilot.wait_for_scheduled_animations()
        await pilot.pause(0.1)

    assert snap_compare(app, terminal_size=(60, 30), run_before=run_before)


def test_snapshot_s18_save_slot_selection_empty(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await pilot.press("down", "enter")
        await wait_for_screen(pilot, SaveSlotSelectionScreen)
        await pilot.pause(0.1)
        await pilot.wait_for_scheduled_animations()
        await pilot.pause(0.1)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s19_save_slot_selection_mixed(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        seed_show_card(pilot.app.state)
        pilot.app.state.run_show()
        pilot.app.session.current_slot_index = 1
        pilot.app.session.pending_slot_name = "Indie Run"
        pilot.app.session.save_current_slot(pilot.app.state)
        await pilot.press("down", "enter")
        await wait_for_screen(pilot, SaveSlotSelectionScreen)
        await pilot.pause(0.1)
        await pilot.wait_for_scheduled_animations()
        await pilot.pause(0.1)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s20_name_save_slot_modal(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await pilot.press("enter")
        await wait_for_screen(pilot, SaveSlotSelectionScreen)
        await pilot.press("enter")
        await wait_for_screen(pilot, NameSaveSlotModal)
        modal = pilot.app.screen
        if isinstance(modal, NameSaveSlotModal):
            modal.cancel_button.focus()
        await pilot.pause(0.1)
        await pilot.wait_for_scheduled_animations()
        await pilot.pause(0.1)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s21_overwrite_save_slot_modal(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        seed_show_card(pilot.app.state)
        pilot.app.state.run_show()
        pilot.app.session.current_slot_index = 1
        pilot.app.session.pending_slot_name = "Indie Run"
        pilot.app.session.save_current_slot(pilot.app.state)
        await pilot.press("enter")
        await wait_for_screen(pilot, SaveSlotSelectionScreen)
        await pilot.press("enter")
        await wait_for_screen(pilot, OverwriteSaveSlotModal)
        await pilot.pause(0.1)
        await pilot.wait_for_scheduled_animations()
        await pilot.pause(0.1)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)
