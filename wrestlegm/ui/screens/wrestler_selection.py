"""Wrestler selection screen."""

from __future__ import annotations

from typing import Callable

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Static

from wrestlegm import constants

from ..formatting import BLOCK_ICON, build_name_cell, build_pop_cell, row_key_to_id
from ..widgets.data_table import EdgeAwareDataTable


class WrestlerSelectionScreen(Screen):
    """Roster picker for assigning a wrestler to a slot side.

    Responsibilities:
    - Render the roster table with stamina/availability hints.
    - Enforce validation rules (duplicates, stamina, already booked).
    - Return the selection to the parent booking screen via callback.
    """

    BINDINGS = [
        ("enter", "select", "Select"),
        ("up", "focus_prev", "Prev"),
        ("down", "focus_next", "Next"),
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(
        self,
        slot_index: int,
        title: str,
        current_ids: set[str],
        booked_ids: set[str],
        on_select: Callable[[str], None],
        allow_low_stamina: bool = False,
    ) -> None:
        """Create a wrestler selection screen for a slot and side."""

        super().__init__()
        self.slot_index = slot_index
        self.title = title
        self.current_ids = current_ids
        self.booked_ids = booked_ids
        self.on_select = on_select
        self.allow_low_stamina = allow_low_stamina
        self.message = Static("")

    def compose(self) -> ComposeResult:
        """Build the wrestler selection layout."""

        yield Static(self.title)
        self.table = EdgeAwareDataTable(
            on_edge_prev=self.action_focus_prev,
            on_edge_next=self.action_focus_next,
        )
        self.table.add_column("Name", key="name")
        self.table.add_column("Sta", key="sta")
        self.table.add_column("Mic", key="mic")
        self.table.add_column("Pop", key="pop")
        for wrestler in self.app.state.roster.values():
            booked = self.app.state.is_wrestler_booked(
                wrestler.id,
                exclude_slot=self.slot_index,
            )
            if wrestler.id in self.booked_ids:
                booked = True
            booked_marker = " 📅" if booked else ""
            self.table.add_row(
                build_name_cell(wrestler.name, wrestler.alignment),
                f"{wrestler.stamina:>3}",
                f"{wrestler.mic_skill:>3}",
                build_pop_cell(wrestler.popularity, wrestler.stamina, booked_marker),
                key=wrestler.id,
            )
        yield self.table
        yield self.message
        with Horizontal():
            self.select_button = Button("Select", id="select")
            self.cancel_button = Button("Cancel", id="cancel")
            yield self.select_button
            yield self.cancel_button
        yield Footer()

    def on_mount(self) -> None:
        """Focus the wrestler list and select the first entry."""

        self.table.focus()
        if self.table.row_count:
            self.table.cursor_coordinate = (0, 0)

    def action_cancel(self) -> None:
        """Close the selection screen without changes."""

        self.app.pop_screen()

    def action_focus_next(self) -> None:
        """Move focus to the next selection control."""

        self._move_focus(1)

    def action_focus_prev(self) -> None:
        """Move focus to the previous selection control."""

        self._move_focus(-1)

    def _move_focus(self, delta: int) -> None:
        """Cycle focus between the list and action buttons."""

        focus_order = [self.table, self.select_button, self.cancel_button]
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

    def action_select(self) -> None:
        """Select the highlighted wrestler if valid."""

        if self.table.cursor_row is None:
            return
        try:
            row_key = self.table.ordered_rows[self.table.cursor_row]
        except IndexError:
            return
        wrestler_id = row_key_to_id(row_key)
        error = self.validate_selection(wrestler_id)
        if error:
            self.message.update(f"{BLOCK_ICON} {error}")
            return
        self.on_select(wrestler_id)
        self.app.pop_screen()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Select the wrestler from table input."""

        if event.data_table is not self.table:
            return
        wrestler_id = row_key_to_id(event.row_key)
        error = self.validate_selection(wrestler_id)
        if error:
            self.message.update(f"{BLOCK_ICON} {error}")
            return
        self.on_select(wrestler_id)
        self.app.pop_screen()

    def validate_selection(self, wrestler_id: str) -> str | None:
        """Return an error message if the wrestler cannot be selected."""

        if wrestler_id in self.current_ids:
            return "Already selected in this match"
        if self.app.state.is_wrestler_booked(wrestler_id, exclude_slot=self.slot_index):
            return "Already booked in another slot"
        wrestler = self.app.state.roster[wrestler_id]
        if not self.allow_low_stamina and wrestler.stamina <= constants.STAMINA_MIN_BOOKABLE:
            return "Not enough stamina"
        return None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle Select and Cancel buttons."""

        if event.button.id == "select":
            self.action_select()
        elif event.button.id == "cancel":
            self.action_cancel()
