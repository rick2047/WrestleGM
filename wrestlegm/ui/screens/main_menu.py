"""Main menu screen for WrestleGM."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, ListItem, ListView, Static

from ..widgets.list_views import EdgeAwareListView


class MainMenuScreen(Screen):
    """Main menu screen for global navigation.

    Responsibilities:
    - Present top-level routes (new game, load game, quit).
    - Dispatch user selection into screen transitions.
    - Keep focus on the menu list for keyboard navigation.
    """

    BINDINGS = [
        ("q", "app.quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Build the main menu layout."""

        yield Static("WrestleGM", classes="section-title")
        self.menu = EdgeAwareListView(
            ListItem(Static("New Game"), id="new-game"),
            ListItem(Static("Load Game"), id="load-game"),
            ListItem(Static("Quit"), id="quit"),
        )
        yield self.menu
        yield Footer()

    def on_mount(self) -> None:
        """Focus the menu list on entry."""

        self.menu.focus()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle selection of menu options."""

        if event.item.id == "new-game":
            from .save_slots import SaveSlotSelectionScreen

            self.app.switch_screen(SaveSlotSelectionScreen(mode="new"))
        elif event.item.id == "load-game":
            from .save_slots import SaveSlotSelectionScreen

            self.app.switch_screen(SaveSlotSelectionScreen(mode="load"))
        elif event.item.id == "quit":
            self.app.exit()
