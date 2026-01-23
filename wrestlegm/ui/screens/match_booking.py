"""Match booking screen."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, ListItem, ListView, Select, Static

from wrestlegm import constants
from wrestlegm.models import Match, MatchTypeDefinition

from ..drafts import BookingDraft
from ..formatting import build_name_cell, match_category_label, match_category_size, slot_label
from ..widgets.list_views import FilteredListView
from ..widgets.safe_select import SafeSelect
from .modals import ConfirmBookingModal
from .wrestler_selection import WrestlerSelectionScreen


class MatchBookingScreen(Screen):
    """Editor for a single match slot.

    Responsibilities:
    - Maintain a local BookingDraft until confirmation.
    - Launch selection screens for wrestlers and match types.
    - Validate the draft and commit it to GameState on confirmation.
    """

    BINDINGS = [
        ("up", "focus_prev", "Prev"),
        ("down", "focus_next", "Next"),
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, slot_index: int, match_category_id: str) -> None:
        """Create a booking screen for a specific slot."""

        super().__init__()
        self.slot_index = slot_index
        self.draft = BookingDraft()
        self.initial_category_id = match_category_id
        self.draft.match_category_id = match_category_id
        self.draft.ensure_size(match_category_size(match_category_id))

    def compose(self) -> ComposeResult:
        """Build the match booking layout."""

        self.header = Static("", classes="section-title")
        yield self.header
        self.detail = Static("", classes="section-title")
        yield self.detail

        max_wrestlers = max(
            (category["size"] for category in constants.MATCH_CATEGORIES.values()),
            default=2,
        )
        self.wrestler_items: list[Static] = []
        self.wrestler_list_items: list[ListItem] = []
        for index in range(max_wrestlers):
            item = Static("")
            self.wrestler_items.append(item)
            self.wrestler_list_items.append(ListItem(item, id=f"field-wrestler-{index}"))
        self.fields = FilteredListView(
            *self.wrestler_list_items,
            is_item_active=lambda item: item.styles.display != "none",
            on_edge_prev=self.action_focus_prev,
            on_edge_next=self.action_focus_next,
        )
        yield self.fields

        self.match_type_label = Static("Stipulation")
        yield self.match_type_label
        self.match_type_select = SafeSelect(
            self._match_type_options_for_category(self.initial_category_id),
            id="match-type",
        )
        yield self.match_type_select

        with Vertical():
            self.confirm_button = Button("Confirm", id="confirm")
            self.clear_button = Button("Clear Slot", id="clear")
            self.cancel_button = Button("Cancel", id="cancel")
            yield self.confirm_button
            yield self.clear_button
            yield self.cancel_button

        yield Footer()

    def on_mount(self) -> None:
        """Load existing slot data and focus the field list."""

        self.fields.focus()
        existing = self.app.state.show_card[self.slot_index]
        if isinstance(existing, Match):
            self.draft.wrestler_ids = list(existing.wrestler_ids)
            self.draft.match_type_id = existing.match_type_id
            self.draft.match_category_id = existing.match_category_id
        if self.initial_category_id is not None:
            self.draft.match_category_id = self.initial_category_id
        self._apply_match_category_change()
        self._refresh_match_type_options()
        self.refresh_view()

    def refresh_view(self) -> None:
        """Update field labels, buttons, and match summary."""

        base_label = f"Book {slot_label(self.slot_index, 'match')}"
        selected_ids = [wrestler_id for wrestler_id in self.draft.wrestler_ids if wrestler_id]
        emojis = self.app.state.rivalry_emojis_for_match(selected_ids)
        header_text = f"{base_label}  {emojis}" if emojis else base_label
        self.header.update(header_text)
        self.detail.update(self.category_label())

        required_count = self.required_wrestler_count()
        for index, item in enumerate(self.wrestler_items):
            list_item = self.wrestler_list_items[index]
            if index < required_count:
                wrestler_id = self.draft.wrestler_ids[index]
                item.update(self.wrestler_field_text(wrestler_id))
                list_item.styles.display = "block"
            else:
                list_item.styles.display = "none"

        if (
            self.fields.index is not None
            and self.fields.index < len(self.wrestler_list_items)
            and self.fields.index >= required_count
        ):
            self.fields.index = 0 if required_count else len(self.wrestler_list_items)

        self.confirm_button.disabled = not self.draft.is_complete(required_count) or bool(
            self.validate_draft()
        )
        self.clear_button.disabled = self.app.state.show_card[self.slot_index] is None

    def wrestler_field_text(self, wrestler_id: str | None) -> str:
        """Render the display text for a wrestler row."""

        if wrestler_id is None:
            return "[ Empty ]"
        wrestler = self.app.state.roster[wrestler_id]
        return build_name_cell(wrestler.name, wrestler.alignment)

    def category_label(self) -> str:
        """Return the current category label for the header detail."""

        if self.draft.match_category_id is None:
            return ""
        return match_category_label(self.draft.match_category_id)

    def required_wrestler_count(self) -> int:
        """Return the required wrestler count for the selected category."""

        if self.draft.match_category_id is None:
            return 0
        return match_category_size(self.draft.match_category_id)

    def _apply_match_category_change(self) -> None:
        """Ensure draft wrestler slots match the selected category."""

        self.draft.ensure_size(self.required_wrestler_count())

    def _available_match_types(self) -> list[MatchTypeDefinition]:
        """Return match types allowed for the selected category."""

        return self._available_match_types_for_category(self.draft.match_category_id)

    def _available_match_types_for_category(
        self, match_category_id: str | None
    ) -> list[MatchTypeDefinition]:
        """Return match types allowed for a specific category."""

        if match_category_id is None:
            return list(self.app.state.match_types.values())
        allowed = []
        for match_type in self.app.state.match_types.values():
            if match_type.allowed_categories is None:
                allowed.append(match_type)
            elif match_category_id in match_type.allowed_categories:
                allowed.append(match_type)
        return allowed

    def _match_type_options_for_category(
        self, match_category_id: str | None
    ) -> list[tuple[str, str]]:
        """Build select options for a category-filtered match type list."""

        return [
            (match_type.name, match_type.id)
            for match_type in self._available_match_types_for_category(match_category_id)
        ]

    def _refresh_match_type_options(self) -> None:
        """Update match type dropdown options based on the category."""

        options = self._match_type_options_for_category(self.draft.match_category_id)
        self.match_type_select.disabled = not options
        valid_ids = {value for _, value in options}
        if self.draft.match_type_id not in valid_ids:
            self.draft.match_type_id = options[0][1] if options else None
        if self.draft.match_type_id is not None:
            self.match_type_select.value = self.draft.match_type_id

    def validate_draft(self) -> list[str]:
        """Return validation errors for the current draft selection."""

        required_count = self.required_wrestler_count()
        if not self.draft.is_complete(required_count):
            return ["incomplete"]
        wrestler_ids = [wrestler_id for wrestler_id in self.draft.wrestler_ids if wrestler_id]
        match = Match(
            wrestler_ids=wrestler_ids,
            match_category_id=self.draft.match_category_id or "",
            match_type_id=self.draft.match_type_id or "",
        )
        return self.app.state.validate_match(match, slot_index=self.slot_index)

    def action_select_field(self) -> None:
        """Open the selection screen for the highlighted field."""

        selected = self.fields.index
        if selected is None:
            return
        required_count = self.required_wrestler_count()
        if selected >= required_count:
            return
        title = f"Select Wrestler ({slot_label(self.slot_index, 'match')} · {selected + 1})"
        current_ids = self._current_ids(exclude_index=selected)
        self.app.push_screen(
            WrestlerSelectionScreen(
                slot_index=self.slot_index,
                title=title,
                current_ids=current_ids,
                booked_ids=self._booked_ids(),
                on_select=lambda wrestler_id: self.set_wrestler(selected, wrestler_id),
            )
        )

    def set_wrestler(self, index: int, wrestler_id: str) -> None:
        """Update the draft with the selected wrestler."""

        if index >= len(self.draft.wrestler_ids):
            return
        self.draft.wrestler_ids[index] = wrestler_id
        self.refresh_view()

    def on_select_changed(self, event: Select.Changed) -> None:
        """Update draft match type when selection changes."""

        if event.select is self.match_type_select and event.value is not None:
            self.draft.match_type_id = event.value
            self.refresh_view()

    def action_cancel(self) -> None:
        """Discard changes and return to the booking hub."""

        slot_index = self.slot_index
        initial_category_id = self.draft.match_category_id or self.initial_category_id
        self.app.pop_screen()
        self.app.open_match_category_selection(
            slot_index,
            initial_category_id,
            on_select=lambda category_id: self.app.open_match_booking(slot_index, category_id),
        )

    def action_focus_next(self) -> None:
        """Move focus to the next booking control."""

        self._move_focus(1)

    def action_focus_prev(self) -> None:
        """Move focus to the previous booking control."""

        self._move_focus(-1)

    def _move_focus(self, delta: int) -> None:
        """Cycle focus between fields and action buttons."""

        focus_order = [
            self.fields,
            self.match_type_select,
            self.confirm_button,
            self.clear_button,
            self.cancel_button,
        ]
        focused = self.app.focused
        if focused not in focus_order:
            focus_order[0].focus()
            return
        index = focus_order.index(focused)
        next_index = index
        for _ in range(len(focus_order)):
            next_index = (next_index + delta) % len(focus_order)
            candidate = focus_order[next_index]
            if candidate is self.fields or not candidate.disabled:
                candidate.focus()
                return

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle Confirm, Clear Slot, and Cancel buttons."""

        if event.button.id == "confirm":
            if self.confirm_button.disabled:
                return
            self.app.push_screen(ConfirmBookingModal(), self.handle_confirmation)
        elif event.button.id == "clear":
            self.app.state.clear_slot(self.slot_index)
            self.app.pop_screen()
        elif event.button.id == "cancel":
            self.app.pop_screen()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle selection from the field list."""

        if event.list_view is not self.fields:
            return
        index = event.index
        if index is None:
            return
        self.fields.index = index
        self.action_select_field()

    def commit_booking(self) -> None:
        """Commit the draft match to the show card."""

        match = Match(
            wrestler_ids=[wrestler_id for wrestler_id in self.draft.wrestler_ids if wrestler_id],
            match_category_id=self.draft.match_category_id or "",
            match_type_id=self.draft.match_type_id or "",
        )
        self.app.state.set_slot(self.slot_index, match)
        self.app.pop_screen()

    def handle_confirmation(self, result: bool | None) -> None:
        """Handle confirmation modal result."""

        if result:
            self.commit_booking()

    def _booked_ids(self) -> set[str]:
        """Return wrestler IDs booked in other slots or current draft."""

        booked: set[str] = set()
        for index, slot in enumerate(self.app.state.show_card):
            if slot is None or index == self.slot_index:
                continue
            if isinstance(slot, Match):
                booked.update(slot.wrestler_ids)
            else:
                booked.add(slot.wrestler_id)
        booked.update(wrestler_id for wrestler_id in self.draft.wrestler_ids if wrestler_id)
        return booked

    def _current_ids(self, exclude_index: int) -> set[str]:
        """Return wrestler IDs selected in the draft excluding the active row."""

        return {
            wrestler_id
            for index, wrestler_id in enumerate(self.draft.wrestler_ids)
            if wrestler_id and index != exclude_index
        }
