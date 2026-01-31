"""Roster overview screen."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import Button, DataTable, Static

from ..formatting import build_name_cell, build_pop_cell, format_money, row_key_to_id
from ..widgets.data_table import EdgeAwareDataTable
from ..widgets.wrestler_view import build_wrestler_view_data
from .standard import StandardScreen
from .wrestler_selection import WrestlerInspectModal


class RosterScreen(StandardScreen):
    """Read-only roster listing.

    Responsibilities:
    - Render current popularity and stamina values.
    - Refresh data on resume to reflect latest show results.
    """

    BINDINGS = [
        ("i", "inspect", "Inspect"),
        ("up", "focus_prev", "Prev"),
        ("down", "focus_next", "Next"),
        ("escape", "back", "Back"),
    ]

    TITLE = "Roster Overview"

    def header_right(self) -> str:
        return f"Money: {format_money(self.app.state.money)}"

    def __init__(self) -> None:
        super().__init__()
        self._inspect_row: int | None = None

    def compose_body(self) -> ComposeResult:
        """Build the roster screen layout."""

        self.table = EdgeAwareDataTable(
            on_edge_prev=self.action_focus_prev,
            on_edge_next=self.action_focus_next,
        )
        self.table.add_column("Name", key="name")
        self.table.add_column("Cost", key="cost")
        self.table.add_column("Sta", key="sta")
        self.table.add_column("Mic", key="mic")
        self.table.add_column("Pop", key="pop")
        yield self.table

    def compose_actions(self) -> list[Button]:
        self.back_button = Button("Back", id="back")
        return [self.back_button]

    async def on_mount(self) -> None:
        """Populate the roster list and focus it."""

        super().on_mount()
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
                f"${self.app.state.wrestler_booking_price(wrestler.id):,}",
                f"{wrestler.stamina:>3}",
                f"{wrestler.mic_skill:>3}",
                build_pop_cell(wrestler.popularity, wrestler.stamina),
                key=wrestler.id,
            )

    def action_back(self) -> None:
        """Close the roster screen."""

        self.app.pop_screen()

    def action_inspect(self) -> None:
        """Open the inspection modal for the highlighted wrestler."""

        if self.table.cursor_row is None:
            return
        try:
            row_key = self.table.ordered_rows[self.table.cursor_row]
        except IndexError:
            return
        wrestler_id = row_key_to_id(row_key)
        wrestler_view = build_wrestler_view_data(self.app.state, wrestler_id)
        rivalries = self._build_rivalry_list(wrestler_id)
        self._inspect_row = self.table.cursor_row
        self.app.push_screen(
            WrestlerInspectModal(wrestler_view, rivalries),
            self._restore_focus_after_inspect,
        )

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

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Inspect the wrestler when the row is selected."""

        if event.data_table is not self.table:
            return
        self.action_inspect()

    def _restore_focus_after_inspect(self, _: object | None = None) -> None:
        """Restore focus to the table after closing the inspect modal."""

        self.table.focus()
        if self._inspect_row is not None and self.table.row_count:
            row = min(self._inspect_row, self.table.row_count - 1)
            self.table.cursor_coordinate = (row, 0)

    def _build_rivalry_list(self, wrestler_id: str) -> list[str]:
        """Build rivalry list entries for the inspected wrestler."""

        entries: list[str] = []
        for opponent_id, opponent in self.app.state.roster.items():
            if opponent_id == wrestler_id:
                continue
            emoji = self.app.state.rivalry_emoji_for_pair(wrestler_id, opponent_id)
            if emoji:
                entries.append(f"{emoji} {opponent.name}")
        return entries

    async def on_screen_resume(self) -> None:
        """Refresh roster data when returning to the screen."""

        super().on_screen_resume()
        await self.refresh_view()
