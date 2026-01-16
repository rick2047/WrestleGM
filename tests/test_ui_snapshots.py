"""UI snapshot tests for canonical screens."""

from __future__ import annotations

from tests.ui_test_utils import (
    TestWrestleGMApp,
    VIEWPORT_SIZE,
    open_booking_hub,
    open_match_booking,
    open_roster,
    seed_show_card,
    select_match_category,
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
    MatchCategorySelectionScreen,
    ResultsScreen,
    SaveSlotSelectionScreen,
    WrestlerSelectionScreen,
)


def test_snapshot_s1_main_menu_default(snap_compare) -> None:
    app = TestWrestleGMApp()
    assert snap_compare(app, terminal_size=VIEWPORT_SIZE)


def test_snapshot_s2_game_hub_default(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await pilot.press("escape")
        await wait_for_screen(pilot, GameHubScreen)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s3_booking_hub_empty(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        await wait_for_screen(pilot, BookingHubScreen)

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

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s5_match_booking_empty(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        await open_match_booking(pilot, 0)
        await select_match_category(pilot, 0)

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
        await select_match_category(pilot, 0)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s7_wrestler_selection_default(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        await open_match_booking(pilot, 0)
        await select_match_category(pilot, 0)
        await pilot.press("enter")
        await wait_for_screen(pilot, WrestlerSelectionScreen)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s8_match_category_selection_default(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        await open_match_booking(pilot, 0)
        await wait_for_screen(pilot, MatchCategorySelectionScreen)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s9_match_booking_confirmation_modal(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await open_booking_hub(pilot)
        await open_match_booking(pilot, 0)
        await select_match_category(pilot, 0)
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

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s10_show_results_default(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        seed_show_card(pilot.app.state)
        pilot.app.state.run_show()
        pilot.app.switch_screen(ResultsScreen())
        await wait_for_screen(pilot, ResultsScreen)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s11_roster_overview_default(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        await pilot.press("escape")
        await wait_for_screen(pilot, GameHubScreen)
        await open_roster(pilot)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s12_booking_hub_rivalry_emojis(snap_compare) -> None:
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

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s13_booking_hub_cooldown_emojis(snap_compare) -> None:
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

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s14_match_booking_rivalry_emojis(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await start_new_game(pilot)
        key = normalize_pair("alpha", "bravo")
        pilot.app.state.rivalry_manager.rivalry_states[key] = RivalryState(
            wrestler_a_id=key[0],
            wrestler_b_id=key[1],
            rivalry_value=4,
        )
        await open_booking_hub(pilot)
        await open_match_booking(pilot, 0)
        await select_match_category(pilot, 0)
        await pilot.press("enter")
        await select_wrestler(pilot, 0)
        await pilot.press("down", "enter")
        await select_wrestler(pilot, 1)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s15_save_slot_selection_empty(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await pilot.press("down", "enter")
        await wait_for_screen(pilot, SaveSlotSelectionScreen)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s16_save_slot_selection_mixed(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        seed_show_card(pilot.app.state)
        pilot.app.state.run_show()
        pilot.app.session.current_slot_index = 1
        pilot.app.session.pending_slot_name = "Indie Run"
        pilot.app.session.save_current_slot(pilot.app.state)
        await pilot.press("down", "enter")
        await wait_for_screen(pilot, SaveSlotSelectionScreen)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s17_name_save_slot_modal(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        await pilot.press("enter")
        await wait_for_screen(pilot, SaveSlotSelectionScreen)
        await pilot.press("enter")
        await wait_for_screen(pilot, NameSaveSlotModal)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)


def test_snapshot_s18_overwrite_save_slot_modal(snap_compare) -> None:
    app = TestWrestleGMApp()

    async def run_before(pilot):
        seed_show_card(pilot.app.state)
        pilot.app.state.run_show()
        pilot.app.session.current_slot_index = 1
        pilot.app.session.pending_slot_name = "My Save"
        pilot.app.session.save_current_slot(pilot.app.state)
        await pilot.press("enter")
        await wait_for_screen(pilot, SaveSlotSelectionScreen)
        await pilot.press("enter")
        await wait_for_screen(pilot, OverwriteSaveSlotModal)

    assert snap_compare(app, terminal_size=VIEWPORT_SIZE, run_before=run_before)
