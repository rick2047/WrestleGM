"""Main menu screen for WrestleGM."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import ListItem, ListView, Static

from ..routes import SAVE_SLOTS
from ..widgets.list_views import EdgeAwareListView
from .standard import StandardScreen


class MainMenuScreen(StandardScreen):
    """Main menu screen for global navigation.

    Responsibilities:
    - Present top-level routes (new game, load game, quit).
    - Dispatch user selection into screen transitions.
    - Keep focus on the menu list for keyboard navigation.
    """

    BINDINGS = [
        ("q", "app.quit", "Quit"),
    ]

    TITLE = "Main Menu"

    def compose_body(self) -> ComposeResult:
        """Build the main menu layout."""

        self.menu = EdgeAwareListView(
            ListItem(Static("New Game"), id="new-game"),
            ListItem(Static("Load Game"), id="load-game"),
            ListItem(Static("Quit"), id="quit"),
        )
        yield self.menu

    def on_mount(self) -> None:
        """Focus the menu list on entry."""

        super().on_mount()
        self.menu.focus()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle selection of menu options."""

        if event.item.id == "new-game":
            self.app.navigate(SAVE_SLOTS, mode="new")
        elif event.item.id == "load-game":
            self.app.navigate(SAVE_SLOTS, mode="load")
        elif event.item.id == "quit":
            self.app.exit()
