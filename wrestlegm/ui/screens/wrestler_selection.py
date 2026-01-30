"""Wrestler selection screen."""

from __future__ import annotations

from typing import Callable

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Static

from wrestlegm import constants, economy

from ..formatting import (
    ALIGNMENT_EMOJI,
    BLOCK_ICON,
    build_pop_cell,
    row_key_to_id,
    truncate_name,
)
from ..widgets.data_table import EdgeAwareDataTable
from ..widgets.wrestler_view import WrestlerView, WrestlerViewConfig, build_wrestler_view_data
from .standard import StandardScreen


class WrestlerSelectionScreen(StandardScreen):
    """Roster picker for assigning a wrestler to a slot side.

    Responsibilities:
    - Render the roster table with stamina/availability hints.
    - Enforce validation rules (duplicates, stamina, already booked).
    - Return the selection to the parent booking screen via callback.
    """

    BINDINGS = [
        ("enter", "select", "Select"),
        ("i", "inspect", "Inspect"),
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
        self._inspect_row: int | None = None

    def header_title(self) -> str:
        return self.title

    def compose_body(self) -> ComposeResult:
        """Build the wrestler selection layout."""

        self.table = EdgeAwareDataTable(
            on_edge_prev=self.action_focus_prev,
            on_edge_next=self.action_focus_next,
        )
        self.table.add_column("Name", key="name")
        self.table.add_column("⭐", key="pop")
        self.table.add_column("Cost", key="cost")
        self.table.add_column("🔋", key="sta")
        self.table.add_column("🎤", key="mic")
        self.table.add_column("Align", key="align")
        for wrestler in self.app.state.roster.values():
            booked = self.app.state.is_wrestler_booked(
                wrestler.id,
                exclude_slot=self.slot_index,
            )
            if wrestler.id in self.booked_ids:
                booked = True
            booked_marker = " 📅" if booked else ""
            self.table.add_row(
                truncate_name(wrestler.name),
                build_pop_cell(wrestler.popularity, wrestler.stamina, booked_marker),
                f"${economy.wrestler_booking_price(wrestler.popularity):,}",
                f"{wrestler.stamina:>3}",
                f"{wrestler.mic_skill:>3}",
                ALIGNMENT_EMOJI.get(wrestler.alignment, ""),
                key=wrestler.id,
            )
        yield self.table
        yield self.message

    def compose_actions(self) -> list[Button]:
        self.select_button = Button("Select", id="select")
        self.cancel_button = Button("Cancel", id="cancel")
        return [self.select_button, self.cancel_button]

    def on_mount(self) -> None:
        """Focus the wrestler list and select the first entry."""

        super().on_mount()
        self.table.focus()
        if self.table.row_count:
            self.table.cursor_coordinate = (0, 0)

    def action_cancel(self) -> None:
        """Close the selection screen without changes."""

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


class WrestlerInspectModal(ModalScreen):
    """Read-only Wrestler View modal for inspection."""

    BINDINGS = [
        ("escape", "close", "Close"),
    ]

    def __init__(self, wrestler: object, rivalries: list[str]) -> None:
        super().__init__()
        self.wrestler = wrestler
        self.rivalries = rivalries

    def compose(self) -> ComposeResult:
        with Vertical(classes="panel inspect-panel"):
            yield Static("Wrestler Details", classes="section-title")
            config = WrestlerViewConfig(
                show_avatar=True,
                show_name=True,
                show_stats=True,
                show_description=True,
                show_rivalry=True,
                rivalry_compact=False,
            )
            yield WrestlerView(self.wrestler, config, rivalries=self.rivalries)
            yield Static("[ Esc to close ]", classes="modal-hint")

    def action_close(self) -> None:
        self.dismiss(result=True)
