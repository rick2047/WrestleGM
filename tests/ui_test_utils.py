"""Utilities for deterministic Textual UI tests."""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from typing import Awaitable, Callable

from textual.app import App
from textual.pilot import Pilot

from wrestlegm import constants
from wrestlegm.data import load_match_types, load_wrestlers
from wrestlegm.models import Match, Promo
from wrestlegm.state import GameState
from wrestlegm.ui import (
    BookingHubScreen,
    ConfirmBookingModal,
    GameHubScreen,
    MainMenuScreen,
    MatchBookingScreen,
    MatchCategorySelectionScreen,
    NameSaveSlotModal,
    PromoBookingScreen,
    ResultsScreen,
    RosterScreen,
    SaveSlotSelectionScreen,
    WrestleGMApp,
    WrestlerSelectionScreen,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "ui"
VIEWPORT_SIZE = (100, 30)
SEED = 2047


class TestWrestleGMApp(WrestleGMApp):
    """WrestleGM app wired to deterministic UI fixtures."""

    __test__ = False

    def __init__(self) -> None:
        App.__init__(self)
        self._save_dir = tempfile.TemporaryDirectory()
        self._wrestlers = load_wrestlers(FIXTURE_DIR / "wrestlers.json")
        self._match_types = load_match_types(FIXTURE_DIR / "match_types.json")
        self.state = GameState(
            self._wrestlers,
            self._match_types,
            seed=SEED,
            save_dir=Path(self._save_dir.name),
        )

    def new_game(self, slot_index: int, slot_name: str) -> None:
        """Start a fresh test session with the fixed seed."""

        self.state.new_game(slot_index, slot_name)
        self.switch_screen(BookingHubScreen())


def run_async(coro: Awaitable[None]) -> None:
    """Run an async coroutine in a sync pytest test."""

    asyncio.run(coro)


def build_test_slots(state: GameState) -> list[Match | Promo]:
    """Build a full show card from the fixture roster."""

    wrestler_ids = list(state.roster.keys())
    match_type_id = next(iter(state.match_types))
    match_category_id = "singles"
    slots: list[Match | Promo] = []
    cursor = 0
    for slot_type in constants.SHOW_SLOT_TYPES:
        if slot_type == "match":
            wrestler_count = constants.MATCH_CATEGORIES[match_category_id]["size"]
            slots.append(
                Match(
                    wrestler_ids=wrestler_ids[cursor : cursor + wrestler_count],
                    match_category_id=match_category_id,
                    match_type_id=match_type_id,
                )
            )
            cursor += wrestler_count
        else:
            slots.append(Promo(wrestler_id=wrestler_ids[cursor]))
            cursor += 1
    return slots


def seed_show_card(state: GameState) -> None:
    """Populate the show card with deterministic matches."""

    slots = build_test_slots(state)
    for index, slot in enumerate(slots):
        state.set_slot(index, slot)


def assert_screen(app: WrestleGMApp, screen_type: type[object]) -> None:
    """Assert the current screen matches the expected type."""

    assert isinstance(app.screen, screen_type)


async def wait_for_screen(
    pilot: Pilot,
    screen_type: type[object] | tuple[type[object], ...],
    attempts: int = 40,
) -> None:
    """Wait for a screen to become active."""

    for _ in range(attempts):
        if isinstance(pilot.app.screen, screen_type):
            return
        await pilot.pause(0.05)
    raise AssertionError(f"Expected screen {screen_type} did not appear.")


async def wait_for_condition(
    pilot: Pilot,
    predicate: Callable[[], bool],
    *,
    attempts: int = 40,
    delay: float = 0.05,
) -> None:
    """Wait for a predicate to become true."""

    for _ in range(attempts):
        if predicate():
            return
        await pilot.pause(delay)
    raise AssertionError("Expected condition was not met.")


async def start_new_game(pilot: Pilot) -> None:
    """Start a new game from the main menu."""

    await pilot.press("enter")
    await wait_for_screen(pilot, SaveSlotSelectionScreen)
    await pilot.press("enter")
    await wait_for_screen(pilot, NameSaveSlotModal)
    modal = pilot.app.screen
    if not isinstance(modal, NameSaveSlotModal):
        raise AssertionError("Expected NameSaveSlotModal")
    modal.name_input.value = "test"
    modal.name_input.focus()
    await wait_for_condition(pilot, lambda: not modal.confirm_button.disabled)
    modal.confirm_button.press()
    await wait_for_screen(pilot, BookingHubScreen)


async def open_booking_hub(pilot: Pilot) -> None:
    """Open the booking hub from the game hub."""

    if isinstance(pilot.app.screen, BookingHubScreen):
        return
    await pilot.press("enter")
    await wait_for_screen(pilot, BookingHubScreen)


async def open_roster(pilot: Pilot) -> None:
    """Open the roster overview from the game hub."""

    await pilot.press("down", "enter")
    await wait_for_screen(pilot, RosterScreen)


async def back_to_game_hub(pilot: Pilot) -> None:
    """Return to the game hub from a child screen."""

    await pilot.press("escape")
    await wait_for_screen(pilot, GameHubScreen)


async def open_match_booking(pilot: Pilot, slot_index: int) -> None:
    """Open match booking for a slot from the booking hub."""

    booking_hub = pilot.app.screen
    if not isinstance(booking_hub, BookingHubScreen):
        raise AssertionError("Expected BookingHubScreen")

    if booking_hub.slot_list.index is None:
        await pilot.press("down")
        await pilot.pause(0.05)

    for _ in range(10):
        if booking_hub.slot_list.index == slot_index:
            break
        await pilot.press("down")
        await pilot.pause(0.05)
    await pilot.press("enter")
    await wait_for_screen(pilot, MatchCategorySelectionScreen)


async def open_promo_booking(pilot: Pilot, slot_index: int) -> None:
    """Open promo booking for a slot from the booking hub."""

    booking_hub = pilot.app.screen
    if not isinstance(booking_hub, BookingHubScreen):
        raise AssertionError("Expected BookingHubScreen")

    if booking_hub.slot_list.index is None:
        await pilot.press("down")
        await pilot.pause(0.05)

    for _ in range(10):
        if booking_hub.slot_list.index == slot_index:
            break
        await pilot.press("down")
        await pilot.pause(0.05)
    await pilot.press("enter")
    await wait_for_screen(pilot, PromoBookingScreen)


async def select_wrestler(pilot: Pilot, row_index: int) -> None:
    """Select a wrestler by row index in the selection screen."""

    await wait_for_screen(pilot, WrestlerSelectionScreen)
    for _ in range(row_index):
        await pilot.press("down")
    await pilot.press("enter")
    await wait_for_screen(pilot, (MatchBookingScreen, PromoBookingScreen))


async def select_match_category(pilot: Pilot, row_index: int = 0) -> None:
    """Select a match category by row index in the selection screen."""

    await wait_for_screen(pilot, MatchCategorySelectionScreen)
    screen = pilot.app.screen
    if isinstance(screen, MatchCategorySelectionScreen):
        screen.list_view.index = row_index
        screen.action_select()
    else:
        for _ in range(row_index):
            await pilot.press("down")
        await pilot.press("enter")
    await wait_for_screen(pilot, MatchBookingScreen)


async def confirm_booking(pilot: Pilot) -> None:
    """Confirm the current match booking draft."""

    screen = pilot.app.screen
    if hasattr(screen, "confirm_button"):
        screen.confirm_button.press()
    else:
        await pilot.press("down")
        await pilot.press("enter")
    await wait_for_screen(pilot, ConfirmBookingModal)
    await pilot.press("enter")
    await wait_for_screen(pilot, BookingHubScreen)
