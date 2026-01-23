"""Match category selection screen."""

from __future__ import annotations

from typing import Callable

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Button, Footer, ListItem, ListView, Static

from wrestlegm import constants

from ..widgets.list_views import EdgeAwareListView


class MatchCategorySelectionScreen(Screen):
    """Match category picker for a slot.

    Responsibilities:
    - Present match categories with wrestler counts.
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
        on_select: Callable[[str], None],
        slot_index: int | None = None,
        initial_category_id: str | None = None,
    ) -> None:
        """Create a match category selection screen."""

        super().__init__()
        self.on_select = on_select
        self.slot_index = slot_index
        self.initial_category_id = initial_category_id

    def compose(self) -> ComposeResult:
        """Build the match category selection layout."""

        yield Static("Select Match Category")
        list_items: list[ListItem] = []
        for category_id in constants.MATCH_CATEGORY_ORDER:
            category = constants.MATCH_CATEGORIES[category_id]
            list_items.append(ListItem(Static(category["name"]), id=category["id"]))
        self.list_view = EdgeAwareListView(
            *list_items,
            on_edge_prev=self.action_focus_prev,
            on_edge_next=self.action_focus_next,
        )
        yield self.list_view
        with Horizontal():
            self.select_button = Button("Select", id="select")
            self.cancel_button = Button("Cancel", id="cancel")
            yield self.select_button
            yield self.cancel_button
        yield Footer()

    def on_mount(self) -> None:
        """Focus the match category list."""

        self.list_view.focus()
        if self.list_view.children:
            if self.initial_category_id is not None:
                for index, child in enumerate(self.list_view.children):
                    if child.id == self.initial_category_id:
                        self.list_view.index = index
                        break
            if self.list_view.index is None:
                self.list_view.index = 0

    def action_select(self) -> None:
        """Select the highlighted match category."""

        index = self.list_view.index
        if index is None:
            return
        selected = self.list_view.children[index]
        if selected.id is None:
            return
        match_category_id = selected.id
        self.app.pop_screen()
        self.on_select(match_category_id)

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

        focus_order = [self.list_view, self.select_button, self.cancel_button]
        focused = self.app.focused
        if focused not in focus_order:
            self.list_view.focus()
            if self.list_view.index is None and self.list_view.children:
                self.list_view.index = 0
            return
        index = focus_order.index(focused)
        next_index = (index + delta) % len(focus_order)
        next_focus = focus_order[next_index]
        if next_focus is self.list_view and self.list_view.index is None and self.list_view.children:
            self.list_view.index = 0
        next_focus.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle Select and Cancel buttons."""

        if event.button.id == "select":
            self.action_select()
        elif event.button.id == "cancel":
            self.action_cancel()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Select the match type from list view input."""

        if event.list_view is not self.list_view:
            return
        match_type_id = event.item.id
        if match_type_id is None:
            return
        self.app.pop_screen()
        self.on_select(match_type_id)
