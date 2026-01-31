"""Match booking screen."""

from __future__ import annotations

from itertools import combinations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, ListItem, ListView, Select, Static

from wrestlegm import constants
from wrestlegm.models import Match, MatchTypeDefinition

from ..drafts import BookingDraft
from ..formatting import format_money, match_category_size, slot_label
from ..widgets import SafeSelect
from ..widgets.list_views import FilteredListView
from ..widgets.wrestler_view import (
    WrestlerView,
    WrestlerViewConfig,
    build_wrestler_view_data,
)
from .modals import ConfirmBookingModal
from .standard import StandardScreen
from .wrestler_selection import WrestlerSelectionScreen


class MatchBookingScreen(StandardScreen):
    """Editor for a single match slot.

    Responsibilities:
    - Maintain a local BookingDraft until confirmation.
    - Launch selection screens for wrestlers and match types.
    - Validate the draft and commit it to GameState on confirmation.
    """

    BINDINGS = [
        ("enter", "select_field", "Select"),
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

    def header_title(self) -> str:
        return slot_label(self.slot_index, "match")

    def header_left(self) -> str:
        selected_ids = [wrestler_id for wrestler_id in self.draft.wrestler_ids if wrestler_id]
        return self.app.state.rivalry_and_cooldown_summary_for_match(selected_ids)

    def header_right(self) -> str:
        return f"Money: {format_money(self.app.state.money)}"

    def compose_body(self) -> ComposeResult:
        """Build the match booking layout."""

        with Vertical(classes="booking-shell"):
            with Vertical(classes="booking-card"):
                with Vertical(classes="match-booking-controls"):
                    with Horizontal(classes="match-booking-controls-row"):
                        with Horizontal(classes="match-booking-control-group"):
                            category_options = self._match_category_options()
                            initial_category = (
                                self.draft.match_category_id
                                or (category_options[0][1] if category_options else None)
                            )
                            self.match_category_select = SafeSelect(
                                category_options,
                                value=initial_category,
                                allow_blank=False,
                                id="match-category",
                                classes="match-category-select",
                            )
                            yield self.match_category_select
                        with Horizontal(classes="match-booking-control-group"):
                            match_type_options = self._match_type_options_for_category(
                                self.initial_category_id
                            )
                            initial_match_type = (
                                match_type_options[0][1] if match_type_options else None
                            )
                            self.match_type_select = SafeSelect(
                                match_type_options,
                                value=initial_match_type,
                                allow_blank=False,
                                id="match-type",
                                classes="match-type-select",
                            )
                            yield self.match_type_select

                yield Static("Wrestlers", classes="booking-section-title")

                max_wrestlers = max(
                    (category["size"] for category in constants.MATCH_CATEGORIES.values()),
                    default=2,
                )
                self.wrestler_views: list[WrestlerView] = []
                self.wrestler_list_items: list[ListItem] = []
                config = WrestlerViewConfig(
                    show_avatar=True,
                    show_name=True,
                    show_stats=True,
                    show_description=False,
                    show_rivalry=True,
                    rivalry_compact=True,
                )
                for index in range(max_wrestlers):
                    view = WrestlerView(None, config)
                    self.wrestler_views.append(view)
                    self.wrestler_list_items.append(
                        ListItem(view, id=f"field-wrestler-{index}")
                    )
                self.fields = FilteredListView(
                    *self.wrestler_list_items,
                    is_item_active=lambda item: item.styles.display != "none",
                    on_edge_prev=self.action_focus_prev,
                    on_edge_next=self.action_focus_next,
                )
                self.fields.add_class("match-wrestlers-scroll")
                yield self.fields

    def compose_actions(self) -> list[Button]:
        self.clear_button = Button("Clear Slot", id="clear")
        self.confirm_button = Button("Confirm", id="confirm")
        self.cancel_button = Button("Cancel", id="cancel")
        return [self.clear_button, self.confirm_button, self.cancel_button]

    def on_mount(self) -> None:
        """Load existing slot data and focus the field list."""

        super().on_mount()
        self.add_class("booking-screen")
        self.fields.focus()
        existing = self.app.state.show_card[self.slot_index]
        if isinstance(existing, Match):
            self.draft.wrestler_ids = list(existing.wrestler_ids)
            self.draft.match_type_id = existing.match_type_id
            self.draft.match_category_id = existing.match_category_id
        if self.initial_category_id is not None:
            self.draft.match_category_id = self.initial_category_id
        self._apply_match_category_change()
        self._refresh_match_category_options()
        self._refresh_match_type_options()
        self.refresh_view()

    def refresh_view(self) -> None:
        """Update field labels, buttons, and match summary."""

        required_count = self.required_wrestler_count()
        for index, view in enumerate(self.wrestler_views):
            list_item = self.wrestler_list_items[index]
            if index < required_count:
                wrestler_id = self.draft.wrestler_ids[index]
                wrestler_view = (
                    build_wrestler_view_data(self.app.state, wrestler_id)
                    if wrestler_id
                    else None
                )
                rivalries = self._rivalry_badges_for_wrestler(wrestler_id)
                view.set_wrestler(wrestler_view, rivalries=rivalries)
                list_item.styles.display = "block"
            else:
                list_item.styles.display = "none"

        if self.fields.index is not None:
            current_item = self.fields.children[self.fields.index]
            wrestler_index = self._wrestler_index_from_item(current_item)
            if wrestler_index is None or wrestler_index >= required_count:
                self._focus_first_wrestler(required_count)

        self.confirm_button.disabled = not self.draft.is_complete(required_count) or bool(
            self.validate_draft()
        )
        self.clear_button.disabled = self.app.state.show_card[self.slot_index] is None
        self.update_header()

    def required_wrestler_count(self) -> int:
        """Return the required wrestler count for the selected category."""

        if self.draft.match_category_id is None:
            return 0
        return match_category_size(self.draft.match_category_id)

    def _apply_match_category_change(self) -> None:
        """Ensure draft wrestler slots match the selected category."""

        self.draft.ensure_size(self.required_wrestler_count())

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

    def _match_category_options(self) -> list[tuple[str, str]]:
        """Return the match category options as wrestler counts."""

        return [
            (str(constants.MATCH_CATEGORIES[category_id]["size"]), category_id)
            for category_id in constants.MATCH_CATEGORY_ORDER
        ]

    def _refresh_match_category_options(self) -> None:
        """Update the match category dropdown options."""

        options = self._match_category_options()
        self.match_category_select.set_options(options)
        self.match_category_select.disabled = not options
        valid_ids = {value for _, value in options}
        if self.draft.match_category_id not in valid_ids:
            self.draft.match_category_id = options[0][1] if options else None
        if self.draft.match_category_id is not None:
            self.match_category_select.value = self.draft.match_category_id

    def _refresh_match_type_options(self) -> None:
        """Update match type dropdown options based on the category."""

        options = self._match_type_options_for_category(self.draft.match_category_id)
        self.match_type_select.set_options(options)
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

        if self.app.focused is self.match_category_select:
            self.match_category_select.action_show_overlay()
            return
        if self.app.focused is self.match_type_select:
            self.match_type_select.action_show_overlay()
            return
        if self.app.focused is not self.fields:
            return
        selected = self.fields.index
        if selected is None:
            return
        item = self.fields.children[selected]
        wrestler_index = self._wrestler_index_from_item(item)
        required_count = self.required_wrestler_count()
        if wrestler_index is None or wrestler_index >= required_count:
            return
        title = (
            f"Select Wrestler ({slot_label(self.slot_index, 'match')} · "
            f"{wrestler_index + 1})"
        )
        current_ids = self._current_ids(exclude_index=wrestler_index)
        self.app.push_screen(
            WrestlerSelectionScreen(
                slot_index=self.slot_index,
                title=title,
                current_ids=current_ids,
                booked_ids=self._booked_ids(),
                on_select=lambda wrestler_id: self.set_wrestler(
                    wrestler_index, wrestler_id
                ),
            )
        )

    def set_wrestler(self, index: int, wrestler_id: str) -> None:
        """Update the draft with the selected wrestler."""

        if index >= len(self.draft.wrestler_ids):
            return
        self.draft.wrestler_ids[index] = wrestler_id
        self.refresh_view()

    def on_select_changed(self, event: Select.Changed) -> None:
        """Update draft selections when a dropdown changes."""

        if event.value is None:
            return
        if event.select is self.match_category_select:
            self.draft.match_category_id = event.value
            self._apply_match_category_change()
            self._refresh_match_type_options()
            self.refresh_view()
        elif event.select is self.match_type_select:
            self.draft.match_type_id = event.value
            self.refresh_view()

    def action_cancel(self) -> None:
        """Discard changes and return to the booking hub."""

        self.app.pop_screen()

    def action_focus_next(self) -> None:
        """Move focus to the next booking control."""

        self._move_focus(1)

    def action_focus_prev(self) -> None:
        """Move focus to the previous booking control."""

        self._move_focus(-1)

    def _move_focus(self, delta: int, selector: str | None = None) -> None:
        """Cycle focus between fields and action buttons."""

        focus_order = [
            self.fields,
            self.match_category_select,
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
            if self.app.state.show_card[self.slot_index] is None:
                return
            self.app.state.clear_slot(self.slot_index)
            self.app.pop_screen()
        elif event.button.id == "cancel":
            self.action_cancel()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle selection from the field list."""

        if event.list_view is not self.fields:
            return
        index = event.index
        if index is None:
            return
        item = self.fields.children[index]
        wrestler_index = self._wrestler_index_from_item(item)
        if wrestler_index is None or wrestler_index >= self.required_wrestler_count():
            return
        self.fields.index = index
        self.action_select_field()

    def commit_booking(self) -> None:
        """Commit the draft match to the show card."""

        match = Match(
            wrestler_ids=[
                wrestler_id for wrestler_id in self.draft.wrestler_ids if wrestler_id
            ],
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

    def _rivalry_badges_for_wrestler(self, wrestler_id: str | None) -> list[str]:
        """Return compact rivalry emoji badges for a wrestler."""

        if not wrestler_id:
            return []
        participants = [wrestler for wrestler in self.draft.wrestler_ids if wrestler]
        if len(participants) < 2:
            return []
        badges: list[str] = []
        for wrestler_a_id, wrestler_b_id in combinations(participants, 2):
            if wrestler_id not in (wrestler_a_id, wrestler_b_id):
                continue
            emoji = self.app.state.rivalry_emoji_for_pair(wrestler_a_id, wrestler_b_id)
            if emoji:
                badges.append(emoji)
        return badges

    def _wrestler_index_from_item(self, item: ListItem) -> int | None:
        if item.id is None:
            return None
        item_id = str(item.id)
        if not item_id.startswith("field-wrestler-"):
            return None
        try:
            return int(item_id.split("-")[-1])
        except ValueError:
            return None

    def _focus_first_wrestler(self, required_count: int) -> None:
        if required_count <= 0:
            return
        for index, item in enumerate(self.fields.children):
            wrestler_index = self._wrestler_index_from_item(item)
            if wrestler_index is not None and wrestler_index < required_count:
                self.fields.index = index
                return
