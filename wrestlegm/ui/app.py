"""Textual app entry point for WrestleGM."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from textual.app import App

from wrestlegm.data import load_match_types, load_wrestlers
from wrestlegm.session import SessionManager
from wrestlegm.state import GameState

from .screens.booking_hub import BookingHubScreen
from .screens.game_hub import GameHubScreen
from .screens.main_menu import MainMenuScreen
from .screens.match_booking import MatchBookingScreen
from .screens.match_category_selection import MatchCategorySelectionScreen
from .screens.modals import ErrorModal
from .screens.promo_booking import PromoBookingScreen
from .screens.results import ResultsScreen
from .screens.roster import RosterScreen
from .screens.save_slots import SaveSlotSelectionScreen
from .screens.simulating import SimulatingScreen


class WrestleGMApp(App):
    """Top-level Textual application entry point.

    Responsibilities:
    - Load data definitions and create the shared GameState instance.
    - Own the application-wide CSS and lifecycle hooks.
    - Push the initial screen into the navigation stack.
    """

    CSS_PATH = Path(__file__).with_name("styles.tcss")

    def __init__(self) -> None:
        """Initialize the app with loaded data and a fresh GameState."""

        super().__init__()
        self._wrestlers = load_wrestlers()
        self._match_types = load_match_types()
        self.session = SessionManager(self._wrestlers, self._match_types)
        self.state = GameState(self._wrestlers, self._match_types)

    def on_mount(self) -> None:
        """Show the main menu at startup."""

        self.push_screen(MainMenuScreen())

    def show_main_menu(self) -> None:
        """Return to the main menu screen."""

        self.switch_screen(MainMenuScreen())

    def show_save_slot_selection(self, mode: str) -> None:
        """Show the save slot selection screen."""

        self.switch_screen(SaveSlotSelectionScreen(mode=mode))

    def show_game_hub(self) -> None:
        """Show the game hub screen."""

        self.switch_screen(GameHubScreen())

    def show_booking_hub(self) -> None:
        """Show the booking hub screen."""

        self.switch_screen(BookingHubScreen())

    def show_roster(self) -> None:
        """Open the roster screen."""

        self.push_screen(RosterScreen())

    def open_match_category_selection(
        self,
        slot_index: int,
        initial_category_id: str | None,
        on_select: Callable[[str], None],
    ) -> None:
        """Open match category selection for a slot."""

        self.push_screen(
            MatchCategorySelectionScreen(
                slot_index=slot_index,
                initial_category_id=initial_category_id,
                on_select=on_select,
            )
        )

    def open_match_booking(self, slot_index: int, match_category_id: str) -> None:
        """Open match booking with a preselected match category."""

        self.push_screen(MatchBookingScreen(slot_index, match_category_id))

    def open_promo_booking(self, slot_index: int) -> None:
        """Open promo booking for a slot."""

        self.push_screen(PromoBookingScreen(slot_index))

    def show_simulating(self) -> None:
        """Show the simulating screen."""

        self.switch_screen(SimulatingScreen())

    def show_results(self) -> None:
        """Show the results screen."""

        self.switch_screen(ResultsScreen())

    def new_game(self, slot_index: int, slot_name: str) -> None:
        """Start a fresh session and show the booking hub."""

        self.state = self.session.new_game(slot_index, slot_name)
        self.show_booking_hub()

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
        self.show_game_hub()
