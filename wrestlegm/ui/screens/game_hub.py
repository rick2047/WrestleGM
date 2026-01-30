"""Game hub screen for an active session."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button

from ..routes import BANKRUPTCY, BOOKING_HUB, MAIN_MENU, ROSTER
from .standard import StandardScreen


class GameHubScreen(StandardScreen):
    """Session-level hub screen.

    Responsibilities:
    - Present session-aware navigation into gameplay screens.
    - Display the current show number.
    - Allow exit back to the main menu.
    """

    BINDINGS = [
        ("enter", "select", "Select"),
        ("up", "focus_prev", "Prev"),
        ("down", "focus_next", "Next"),
        ("q", "app.quit", "Quit"),
    ]

    TITLE = "Game Hub"

    def compose_body(self) -> ComposeResult:
        """Build the game hub layout."""

        with Vertical(classes="menu-button-group"):
            self.current_show_button = Button("", id="current-show", classes="menu-button")
            self.roster_button = Button("Roster Overview", id="roster", classes="menu-button")
            self.exit_button = Button("Exit to Main Menu", id="exit", classes="menu-button")
            yield self.current_show_button
            yield self.roster_button
            yield self.exit_button

    def on_mount(self) -> None:
        """Focus the menu list and refresh labels."""

        super().on_mount()
        self.refresh_view()
        self.current_show_button.focus()

    def refresh_view(self) -> None:
        """Update the current show text."""

        self.current_show_button.label = (
            "Book Current Show\n"
            f"[dim]Show #{self.app.state.show_index}[/dim]"
        )

    def on_screen_resume(self) -> None:
        """Refresh the hub labels after returning."""

        super().on_screen_resume()
        self.refresh_view()
        self.current_show_button.focus()

    def action_select(self) -> None:
        """Activate the currently focused hub option."""

        focused = self.app.focused
        if isinstance(focused, Button):
            self._route_selection(focused.id)
            return
        self._route_selection(self.current_show_button.id)

    def action_focus_next(self) -> None:
        """Move focus to the next hub button."""

        self._move_focus(1)

    def action_focus_prev(self) -> None:
        """Move focus to the previous hub button."""

        self._move_focus(-1)

    def _move_focus(self, delta: int) -> None:
        """Cycle focus across hub buttons."""

        focus_order = [
            self.current_show_button,
            self.roster_button,
            self.exit_button,
        ]
        focused = self.app.focused
        if focused not in focus_order:
            self.current_show_button.focus()
            return
        index = focus_order.index(focused)
        focus_order[(index + delta) % len(focus_order)].focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle hub button presses."""

        self._route_selection(event.button.id)

    def _route_selection(self, item_id: str | None) -> None:
        """Route the selected menu option to the target screen."""

        if item_id == "current-show":
            if self.app.state.is_bankrupt():
                self.app.navigate(BANKRUPTCY)
            else:
                self.app.navigate(BOOKING_HUB)
        elif item_id == "roster":
            self.app.navigate(ROSTER)
        elif item_id == "exit":
            self.app.navigate(MAIN_MENU)
