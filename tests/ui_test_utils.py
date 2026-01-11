"""Utilities for deterministic Textual UI tests."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Awaitable

from textual.app import App
from textual.pilot import Pilot

from wrestlegm.data import load_match_types, load_wrestlers
from wrestlegm.models import Match
from wrestlegm.state import GameState
from wrestlegm.ui import (
    BookingHubScreen,
    ConfirmBookingModal,
    GameHubScreen,
    MainMenuScreen,
    MatchBookingScreen,
    MatchTypeSelectionScreen,
    ResultsScreen,
    RosterScreen,
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
        self._wrestlers = load_wrestlers(FIXTURE_DIR / "wrestlers.json")
        self._match_types = load_match_types(FIXTURE_DIR / "match_types.json")
        self.state = GameState(self._wrestlers, self._match_types, seed=SEED)

    def new_game(self) -> None:
        """Start a fresh test session with the fixed seed."""

        self.state = GameState(self._wrestlers, self._match_types, seed=SEED)
        self.switch_screen(GameHubScreen())


def run_async(coro: Awaitable[None]) -> None:
    """Run an async coroutine in a sync pytest test."""

    asyncio.run(coro)


def build_test_matches(state: GameState) -> list[Match]:
    """Build a full show card from the fixture roster."""

    wrestler_ids = list(state.roster.keys())
    match_type_id = next(iter(state.match_types))
    return [
        Match(wrestler_a_id=wrestler_ids[0], wrestler_b_id=wrestler_ids[1], match_type_id=match_type_id),
        Match(wrestler_a_id=wrestler_ids[2], wrestler_b_id=wrestler_ids[3], match_type_id=match_type_id),
        Match(wrestler_a_id=wrestler_ids[4], wrestler_b_id=wrestler_ids[5], match_type_id=match_type_id),
    ]


def seed_show_card(state: GameState) -> None:
    """Populate the show card with deterministic matches."""

    matches = build_test_matches(state)
    for index, match in enumerate(matches):
        state.set_slot(index, match)


def assert_screen(app: WrestleGMApp, screen_type: type[object]) -> None:
    """Assert the current screen matches the expected type."""

    assert isinstance(app.screen, screen_type)


async def wait_for_screen(pilot: Pilot, screen_type: type[object], attempts: int = 40) -> None:
    """Wait for a screen to become active."""

    for _ in range(attempts):
        if isinstance(pilot.app.screen, screen_type):
            return
        await pilot.pause(0.05)
    raise AssertionError(f"Expected screen {screen_type} did not appear.")


async def start_new_game(pilot: Pilot) -> None:
    """Start a new game from the main menu."""

    await pilot.press("enter")
    await wait_for_screen(pilot, GameHubScreen)


async def open_booking_hub(pilot: Pilot) -> None:
    """Open the booking hub from the game hub."""

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
    await wait_for_screen(pilot, MatchBookingScreen)


async def select_wrestler(pilot: Pilot, row_index: int) -> None:
    """Select a wrestler by row index in the selection screen."""

    await wait_for_screen(pilot, WrestlerSelectionScreen)
    for _ in range(row_index):
        await pilot.press("down")
    await pilot.press("enter")
    await wait_for_screen(pilot, MatchBookingScreen)


async def select_match_type(pilot: Pilot, row_index: int = 0) -> None:
    """Select a match type by row index in the selection screen."""

    await wait_for_screen(pilot, MatchTypeSelectionScreen)
    for _ in range(row_index):
        await pilot.press("down")
    await pilot.press("enter")
    await wait_for_screen(pilot, MatchBookingScreen)


async def confirm_booking(pilot: Pilot) -> None:
    """Confirm the current match booking draft."""

    await pilot.press("down")
    await pilot.press("enter")
    await wait_for_screen(pilot, ConfirmBookingModal)
    await pilot.press("enter")
    await wait_for_screen(pilot, BookingHubScreen)
