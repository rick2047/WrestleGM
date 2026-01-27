"""Application header widget."""

from __future__ import annotations

from dataclasses import dataclass

from rich.table import Table
from rich.text import Text
from textual.reactive import reactive
from textual.widgets import Header


@dataclass(frozen=True)
class HeaderState:
    """Current header render state."""

    title: str
    left: str = ""
    right: str = ""


class WrestleHeader(Header):
    """A Textual Header that renders a centered screen title with optional side context."""

    state: reactive[HeaderState] = reactive(HeaderState(title=""))

    def __init__(self, *, side_width: int = 22) -> None:
        super().__init__(show_clock=False)
        self.side_width = side_width

    def set_state(self, state: HeaderState) -> None:
        self.state = state

    def render(self) -> Table:
        left = Text(self.state.left, style="dim")
        title = Text(self.state.title, style="bold")
        right = Text(self.state.right, style="dim")

        left.truncate(self.side_width, overflow="ellipsis")
        right.truncate(self.side_width, overflow="ellipsis")

        table = Table.grid(expand=True)
        table.add_column(width=self.side_width, overflow="ellipsis", no_wrap=True, justify="left")
        table.add_column(ratio=1, overflow="ellipsis", no_wrap=True, justify="center")
        table.add_column(width=self.side_width, overflow="ellipsis", no_wrap=True, justify="right")
        table.add_row(left, title, right)
        return table
