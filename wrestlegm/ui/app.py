"""Textual app entry point for WrestleGM."""

from __future__ import annotations

from pathlib import Path

from textual.app import App

from wrestlegm.data import load_match_types, load_wrestlers
from wrestlegm.session import SessionManager
from wrestlegm.state import GameState

from .screens.main_menu import MainMenuScreen


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

    def new_game(self, slot_index: int, slot_name: str) -> None:
        """Start a fresh session and show the booking hub."""

        from .screens.booking_hub import BookingHubScreen

        self.state = self.session.new_game(slot_index, slot_name)
        self.switch_screen(BookingHubScreen())

    def load_game(self, slot_index: int) -> None:
        """Load a saved session and show the game hub."""

        from .screens.game_hub import GameHubScreen
        from .screens.modals import ErrorModal

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
        self.switch_screen(GameHubScreen())
