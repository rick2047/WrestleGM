"""Roster overview screen."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Footer, Static

from ..formatting import build_name_cell, build_pop_cell
from ..widgets.data_table import EdgeAwareDataTable


class RosterScreen(Screen):
    """Read-only roster listing.

    Responsibilities:
    - Render current popularity and stamina values.
    - Refresh data on resume to reflect latest show results.
    """

    BINDINGS = [
        ("up", "focus_prev", "Prev"),
        ("down", "focus_next", "Next"),
        ("escape", "back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        """Build the roster screen layout."""

        yield Static("Roster Overview", classes="section-title")
        self.table = EdgeAwareDataTable(
            on_edge_prev=self.action_focus_prev,
            on_edge_next=self.action_focus_next,
        )
        self.table.add_column("Name", key="name")
        self.table.add_column("Sta", key="sta")
        self.table.add_column("Mic", key="mic")
        self.table.add_column("Pop", key="pop")
        yield self.table
        self.back_button = Button("Back", id="back")
        yield self.back_button
        yield Footer()

    async def on_mount(self) -> None:
        """Populate the roster list and focus it."""

        await self.refresh_view()
        self.table.focus()
        if self.table.row_count:
            self.table.cursor_coordinate = (0, 0)

    async def refresh_view(self) -> None:
        """Rebuild roster rows from current state."""

        self.table.clear()
        for wrestler in self.app.state.roster.values():
            self.table.add_row(
                build_name_cell(wrestler.name, wrestler.alignment),
                f"{wrestler.stamina:>3}",
                f"{wrestler.mic_skill:>3}",
                build_pop_cell(wrestler.popularity, wrestler.stamina),
                key=wrestler.id,
            )

    def action_back(self) -> None:
        """Close the roster screen."""

        self.app.pop_screen()

    def action_focus_next(self) -> None:
        """Move focus to the next roster control."""

        self._move_focus(1)

    def action_focus_prev(self) -> None:
        """Move focus to the previous roster control."""

        self._move_focus(-1)

    def _move_focus(self, delta: int) -> None:
        """Cycle focus between the roster list and Back button."""

        focus_order = [self.table, self.back_button]
        focused = self.app.focused
        if focused not in focus_order:
            self.table.focus()
            if self.table.cursor_row is None and self.table.row_count:
                self.table.cursor_coordinate = (0, 0)
            return
        index = focus_order.index(focused)
        next_index = (index + delta) % len(focus_order)
        next_focus = focus_order[next_index]
        if next_focus is self.table and self.table.cursor_row is None and self.table.row_count:
            self.table.cursor_coordinate = (0, 0)
        next_focus.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle Back button presses."""

        if event.button.id == "back":
            self.action_back()

    async def on_screen_resume(self) -> None:
        """Refresh roster data when returning to the screen."""

        await self.refresh_view()
