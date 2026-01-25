"""Viewport guard screen for minimum terminal size."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Static


class GuardScreen(Screen):
    """Non-interactive guard screen when terminal is too small."""

    MIN_COLUMNS = 60
    MIN_ROWS = 30

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        self.message = Static("", classes="guard-message")
        yield self.message
        yield Footer()

    def on_mount(self) -> None:
        self._update_message()

    def on_resize(self) -> None:
        self._update_message()

    def action_quit(self) -> None:
        self.app.exit()

    def _update_message(self) -> None:
        size = self.app.size
        cols = size.width
        rows = size.height
        self.message.update(
            "Terminal size too small "
            f"(need {self.MIN_COLUMNS}x{self.MIN_ROWS}).\n"
            f"Current size: {cols}x{rows}.\n"
            "Resize your terminal and restart the app.\n\n"
            "[ Q ] Quit"
        )
