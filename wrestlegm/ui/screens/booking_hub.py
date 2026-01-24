"""Show overview and booking hub for the current card."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, ListItem, ListView, Static

from wrestlegm import constants
from wrestlegm.models import Match

from ..formatting import build_match_participants, match_category_label, slot_label
from ..routes import (
    GAME_HUB,
    MATCH_BOOKING,
    PROMO_BOOKING,
    SIMULATING,
)
from ..widgets.list_views import EdgeAwareListView


class BookingHubScreen(Screen):
    """Show overview and booking hub for the current card.

    Responsibilities:
    - Display the current show number and slot summaries.
    - Allow the user to open a slot editor.
    - Gate Run Show based on validation.
    """

    BINDINGS = [
        ("enter", "edit_slot", "Edit"),
        ("r", "run_show", "Run Show"),
        ("up", "focus_prev", "Prev"),
        ("down", "focus_next", "Next"),
        ("escape", "back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        """Build the booking hub layout."""

        yield Static("WrestleGM", classes="section-title")
        self.show_header = Static("", classes="section-title")
        yield self.show_header

        self.slot_items: list[Static] = []
        slot_list_items: list[ListItem] = []
        for index in range(constants.SHOW_SLOT_COUNT):
            slot_static = Static("", id=f"slot-{index}")
            self.slot_items.append(slot_static)
            slot_list_items.append(ListItem(slot_static, id=f"slot-item-{index}"))
        self.slot_list = EdgeAwareListView(
            *slot_list_items,
            on_edge_prev=self.action_focus_prev,
            on_edge_next=self.action_focus_next,
        )
        yield self.slot_list

        with Vertical():
            self.run_button = Button("Run Show", id="run-show")
            self.run_button.disabled = True
            self.back_button = Button("Back", id="back")
            yield self.run_button
            yield self.back_button

        yield Footer()

    def on_mount(self) -> None:
        """Focus the slot list and refresh the view."""

        self.slot_list.focus()
        self.refresh_view()

    def refresh_view(self) -> None:
        """Update slot text and Run Show enablement."""

        self.show_header.update(f"Show #{self.app.state.show_index}")
        for index, slot_static in enumerate(self.slot_items):
            slot_static.update(self.slot_text(index))
        self.run_button.disabled = bool(self.app.state.validate_show())

    def slot_text(self, index: int) -> str:
        """Render the slot summary text for a match slot."""

        slot = self.app.state.show_card[index]
        slot_type = self.app.state.slot_type(index)
        label = slot_label(index, slot_type)
        if slot is None:
            return f"{label}\n[ Empty ]"
        if isinstance(slot, Match):
            wrestlers = [self.app.state.roster[w_id] for w_id in slot.wrestler_ids]
            match_type = self.app.state.match_types.get(slot.match_type_id)
            match_type_name = match_type.name if match_type else "Unknown"
            category_name = match_category_label(slot.match_category_id)
            emojis = self.app.state.rivalry_emojis_for_match(slot.wrestler_ids)
            label_text = f"{label}  {emojis}" if emojis else label
            return (
                f"{label_text}\n{build_match_participants(wrestlers)}\n"
                f"{category_name} · {match_type_name}"
            )
        wrestler = self.app.state.roster[slot.wrestler_id]
        return f"{label}\n{wrestler.name}"

    def action_edit_slot(self) -> None:
        """Open the booking screen for the selected slot."""

        index = self.slot_list.index
        if index is None:
            return
        if self.app.state.slot_type(index) == "match":
            self.open_match_booking(index)
        else:
            self.app.navigate(PROMO_BOOKING, slot_index=index)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle slot selection from the list view."""

        if event.list_view is not self.slot_list:
            return
        index = event.index
        if index is None:
            return
        if self.app.state.slot_type(index) == "match":
            self.open_match_booking(index)
        else:
            self.app.navigate(PROMO_BOOKING, slot_index=index)

    def open_match_booking(self, slot_index: int) -> None:
        """Open match booking with the existing or default category."""

        existing = self.app.state.show_card[slot_index]
        if isinstance(existing, Match):
            match_category_id = existing.match_category_id
        else:
            match_category_id = constants.MATCH_CATEGORY_ORDER[0]
        self.app.navigate(
            MATCH_BOOKING,
            slot_index=slot_index,
            match_category_id=match_category_id,
        )

    def action_run_show(self) -> None:
        """Run the show if the current card is valid."""

        if self.app.state.validate_show():
            return
        self.app.navigate(SIMULATING)

    def action_back(self) -> None:
        """Return to the game hub."""

        self.app.navigate(GAME_HUB)

    def action_focus_next(self) -> None:
        """Move focus to the next booking hub control."""

        self._move_focus(1)

    def action_focus_prev(self) -> None:
        """Move focus to the previous booking hub control."""

        self._move_focus(-1)

    def _move_focus(self, delta: int) -> None:
        """Cycle focus between the slot list and action buttons."""

        focus_order = [self.slot_list, self.run_button, self.back_button]
        focused = self.app.focused
        if focused not in focus_order:
            focus_order[0].focus()
            return
        index = focus_order.index(focused)
        next_index = index
        for _ in range(len(focus_order)):
            next_index = (next_index + delta) % len(focus_order)
            candidate = focus_order[next_index]
            if candidate is self.slot_list or not candidate.disabled:
                if candidate is self.slot_list and focused is not self.slot_list:
                    self.slot_list.index = 0
                candidate.focus()
                return

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle Run Show and Back button presses."""

        if event.button.id == "run-show":
            self.action_run_show()
        elif event.button.id == "back":
            self.action_back()

    def on_screen_resume(self) -> None:
        """Refresh slot details after returning to the hub."""

        self.refresh_view()
