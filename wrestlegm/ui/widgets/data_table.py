"""Custom DataTable with edge-aware navigation."""

from __future__ import annotations

from typing import Callable

from textual.widgets import DataTable


class EdgeAwareDataTable(DataTable):
    """DataTable that can hand off focus when the cursor hits an edge."""

    def __init__(
        self,
        *,
        on_edge_prev: Callable[[], None] | None = None,
        on_edge_next: Callable[[], None] | None = None,
    ) -> None:
        super().__init__()
        self._on_edge_prev = on_edge_prev
        self._on_edge_next = on_edge_next
        self.cursor_type = "row"

    def action_cursor_down(self) -> None:
        """Move focus to the next widget when already at the last row."""

        if self.cursor_row is not None and self.cursor_row >= self.row_count - 1:
            if self._on_edge_next is not None:
                self._on_edge_next()
                return
        super().action_cursor_down()

    def action_cursor_up(self) -> None:
        """Move focus to the previous widget when already at the first row."""

        if self.cursor_row is not None and self.cursor_row <= 0:
            if self._on_edge_prev is not None:
                self._on_edge_prev()
                return
        super().action_cursor_up()
