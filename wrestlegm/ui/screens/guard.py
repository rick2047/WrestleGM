"""Viewport guard screen for minimum terminal size."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import Button, Static

from .standard import StandardScreen


class GuardScreen(StandardScreen):
    """Non-interactive guard screen when terminal is too small."""

    MIN_COLUMNS = 60
    MIN_ROWS = 30

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    TITLE = "Viewport Guard"

    def compose_body(self) -> ComposeResult:
        self.message = Static("", classes="guard-message")
        yield self.message

    def compose_actions(self) -> list[Button]:
        self.quit_button = Button("Quit", id="quit")
        return [self.quit_button]

    def on_mount(self) -> None:
        super().on_mount()
        self._update_message()
        self.quit_button.focus()

    def on_resize(self) -> None:
        self._update_message()

    def action_quit(self) -> None:
        self.app.exit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.action_quit()

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
