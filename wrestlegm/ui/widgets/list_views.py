"""Custom list views with edge-aware navigation."""

from __future__ import annotations

from typing import Callable

from textual.widgets import ListItem, ListView


class EdgeAwareListView(ListView):
    """ListView that can hand off focus when the cursor hits an edge."""

    def __init__(
        self,
        *items: ListItem,
        on_edge_prev: Callable[[], None] | None = None,
        on_edge_next: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(*items)
        self._on_edge_prev = on_edge_prev
        self._on_edge_next = on_edge_next

    def action_cursor_down(self) -> None:
        """Move focus to the next widget when already at the last row."""

        if self.index is not None and self.index >= len(self.children) - 1:
            if self._on_edge_next is not None:
                self._on_edge_next()
                return
            if self.children:
                self.index = 0
                return
        super().action_cursor_down()

    def action_cursor_up(self) -> None:
        """Move focus to the previous widget when already at the first row."""

        if self.index is not None and self.index <= 0:
            if self._on_edge_prev is not None:
                self._on_edge_prev()
                return
            if self.children:
                self.index = len(self.children) - 1
                return
        super().action_cursor_up()


class FilteredListView(EdgeAwareListView):
    """ListView that skips non-visible items during navigation."""

    def __init__(
        self,
        *items: ListItem,
        is_item_active: Callable[[ListItem], bool],
        on_edge_prev: Callable[[], None] | None = None,
        on_edge_next: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(*items, on_edge_prev=on_edge_prev, on_edge_next=on_edge_next)
        self._is_item_active = is_item_active

    def _active_indices(self) -> list[int]:
        return [
            index
            for index, item in enumerate(self.children)
            if self._is_item_active(item)
        ]

    def action_cursor_down(self) -> None:
        active = self._active_indices()
        if not active:
            return
        if self.index is None:
            self.index = active[0]
            return
        if self.index == active[-1]:
            if self._on_edge_next is not None:
                self._on_edge_next()
                return
            self.index = active[0]
            return
        for index in active:
            if index > (self.index or 0):
                self.index = index
                return

    def action_cursor_up(self) -> None:
        active = self._active_indices()
        if not active:
            return
        if self.index is None:
            self.index = active[-1]
            return
        if self.index == active[0]:
            if self._on_edge_prev is not None:
                self._on_edge_prev()
                return
            self.index = active[-1]
            return
        for index in reversed(active):
            if index < (self.index or 0):
                self.index = index
                return
