"""Main menu screen for WrestleGM."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button

from ..routes import SAVE_SLOTS
from .standard import StandardScreen


class MainMenuScreen(StandardScreen):
    """Main menu screen for global navigation.

    Responsibilities:
    - Present top-level routes (new game, load game, quit).
    - Dispatch user selection into screen transitions.
    - Keep focus on the menu list for keyboard navigation.
    """

    BINDINGS = [
        ("enter", "select", "Select"),
        ("up", "focus_prev", "Prev"),
        ("down", "focus_next", "Next"),
        ("q", "app.quit", "Quit"),
    ]

    TITLE = "Main Menu"

    def compose_body(self) -> ComposeResult:
        """Build the main menu layout."""

        with Vertical(classes="menu-button-group"):
            self.new_game_button = Button("New Game", id="new-game", classes="menu-button")
            self.load_game_button = Button("Load Game", id="load-game", classes="menu-button")
            self.quit_button = Button("Quit", id="quit", classes="menu-button")
            yield self.new_game_button
            yield self.load_game_button
            yield self.quit_button

    def action_select(self) -> None:
        """Activate the currently focused menu option."""

        focused = self.app.focused
        if isinstance(focused, Button):
            self._handle_action(focused.id)
            return
        self._handle_action(self.new_game_button.id)

    def action_focus_next(self) -> None:
        """Move focus to the next menu button."""

        self._move_focus(1)

    def action_focus_prev(self) -> None:
        """Move focus to the previous menu button."""

        self._move_focus(-1)

    def _move_focus(self, delta: int) -> None:
        """Cycle focus across menu buttons."""

        focus_order = [self.new_game_button, self.load_game_button, self.quit_button]
        focused = self.app.focused
        if focused not in focus_order:
            self.new_game_button.focus()
            return
        index = focus_order.index(focused)
        focus_order[(index + delta) % len(focus_order)].focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses for menu navigation."""

        self._handle_action(event.button.id)

    def _handle_action(self, button_id: str | None) -> None:
        if button_id == "new-game":
            self.app.navigate(SAVE_SLOTS, mode="new")
        elif button_id == "load-game":
            self.app.navigate(SAVE_SLOTS, mode="load")
        elif button_id == "quit":
            self.app.exit()
