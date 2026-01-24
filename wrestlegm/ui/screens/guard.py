"""Viewport guard screen for minimum terminal size."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Static


class GuardScreen(Screen):
    """Non-interactive guard screen when terminal is too small."""

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Static(
            "Terminal size too small (need 70x40).\n"
            "Resize your terminal and restart the app.\n\n"
            "[ Q ] Quit",
            classes="guard-message",
        )
        yield Footer()

    def action_quit(self) -> None:
        self.app.exit()
