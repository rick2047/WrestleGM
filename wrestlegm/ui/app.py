"""Textual app entry point for WrestleGM."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from textual.app import App
from textual.screen import Screen

from wrestlegm.data import load_match_types, load_wrestlers
from wrestlegm.session import SessionManager
from wrestlegm.state import GameState

from .routes import (
    BOOKING_HUB,
    GAME_HUB,
    MAIN_MENU,
    MATCH_BOOKING,
    PROMO_BOOKING,
    RESULTS,
    ROSTER,
    SAVE_SLOTS,
    SIMULATING,
)
from .screens.booking_hub import BookingHubScreen
from .screens.guard import GuardScreen
from .screens.game_hub import GameHubScreen
from .screens.main_menu import MainMenuScreen
from .screens.match_booking import MatchBookingScreen
from .screens.modals import ErrorModal
from .screens.promo_booking import PromoBookingScreen
from .screens.results import ResultsScreen
from .screens.roster import RosterScreen
from .screens.save_slots import SaveSlotSelectionScreen
from .screens.simulating import SimulatingScreen


STYLES_PATH = Path(__file__).with_name("styles.tcss")


class WrestleGMApp(App):
    """Top-level Textual application entry point.

    Responsibilities:
    - Load data definitions and create the shared GameState instance.
    - Own the application-wide CSS and lifecycle hooks.
    - Push the initial screen into the navigation stack.
    """

    CSS_PATH = STYLES_PATH

    def __init__(self) -> None:
        """Initialize the app with loaded data and a fresh GameState."""

        super().__init__()
        self._wrestlers = load_wrestlers()
        self._match_types = load_match_types()
        self.session = SessionManager(self._wrestlers, self._match_types)
        self.state = GameState(self._wrestlers, self._match_types)

    def on_mount(self) -> None:
        """Show the main menu at startup."""
        if self.size.width < 70 or self.size.height < 40:
            self.push_screen(GuardScreen())
            return
        self.push_screen(MainMenuScreen())

    def new_game(self, slot_index: int, slot_name: str) -> None:
        """Start a fresh session and show the booking hub."""

        self.state = self.session.new_game(slot_index, slot_name)
        self.navigate(BOOKING_HUB)

    def load_game(self, slot_index: int) -> None:
        """Load a saved session and show the game hub."""

        try:
            self.state = self.session.load_game(slot_index)
        except ValueError as exc:
            message = "Unable to load save."
            if str(exc) == "unsupported_save_version":
                message = "Save version unsupported."
            elif str(exc) == "corrupt_save_file":
                message = "Save file is corrupt."
            elif str(exc) in {"empty_slot", "missing_save_file"}:
                message = "Save file is missing."
            self.push_screen(ErrorModal(message=message))
            return
        self.navigate(GAME_HUB)

    def navigate(self, route: str, **kwargs: object) -> None:
        """Navigate to a registered screen route."""

        target = ROUTES[route]
        screen = target.factory(**kwargs)
        if target.mode == "push":
            self.push_screen(screen)
        else:
            self.switch_screen(screen)


@dataclass(frozen=True)
class Route:
    mode: str
    factory: Callable[..., Screen]


ROUTES: dict[str, Route] = {
    MAIN_MENU: Route("switch", lambda **_: MainMenuScreen()),
    SAVE_SLOTS: Route("switch", lambda mode: SaveSlotSelectionScreen(mode=mode)),
    GAME_HUB: Route("switch", lambda **_: GameHubScreen()),
    BOOKING_HUB: Route("switch", lambda **_: BookingHubScreen()),
    ROSTER: Route("push", lambda **_: RosterScreen()),
    MATCH_BOOKING: Route(
        "push",
        lambda slot_index, match_category_id: MatchBookingScreen(
            slot_index, match_category_id
        ),
    ),
    PROMO_BOOKING: Route("push", lambda slot_index: PromoBookingScreen(slot_index)),
    SIMULATING: Route("switch", lambda **_: SimulatingScreen()),
    RESULTS: Route("switch", lambda **_: ResultsScreen()),
}
