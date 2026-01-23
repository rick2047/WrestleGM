"""Game hub screen for an active session."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, ListItem, ListView, Static

from ..routes import BOOKING_HUB, MAIN_MENU, ROSTER
from ..widgets.list_views import EdgeAwareListView


class GameHubScreen(Screen):
    """Session-level hub screen.

    Responsibilities:
    - Present session-aware navigation into gameplay screens.
    - Display the current show number.
    - Allow exit back to the main menu.
    """

    BINDINGS = [
        ("enter", "select", "Select"),
        ("q", "app.quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Build the game hub layout."""

        yield Static("WrestleGM", classes="section-title")
        yield Static("Game Hub", classes="section-title")

        self.current_show = Static("")
        self.roster = Static("Roster Overview\n")
        self.exit = Static("Exit to Main Menu\n")

        self.menu = EdgeAwareListView(
            ListItem(self.current_show, id="current-show"),
            ListItem(self.roster, id="roster"),
            ListItem(self.exit, id="exit"),
        )
        yield self.menu
        yield Footer()

    def on_mount(self) -> None:
        """Focus the menu list and refresh labels."""

        self.menu.focus()
        if self.menu.index is None:
            self.menu.index = 0
        self.refresh_view()

    def refresh_view(self) -> None:
        """Update the current show text."""

        self.current_show.update(
            "Book Current Show\n"
            f"[dim]Show #{self.app.state.show_index}[/dim]"
        )

    def on_screen_resume(self) -> None:
        """Refresh the hub labels after returning."""

        self.menu.focus()
        self.menu.index = 0
        self.refresh_view()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle hub option selection."""

        self._route_selection(event.item.id)

    def _route_selection(self, item_id: str | None) -> None:
        """Route the selected menu option to the target screen."""

        if item_id == "current-show":
            self.app.navigate(BOOKING_HUB)
        elif item_id == "roster":
            self.app.navigate(ROSTER)
        elif item_id == "exit":
            self.app.navigate(MAIN_MENU)
