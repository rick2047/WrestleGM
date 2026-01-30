"""Bankruptcy game over screen."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Static

from ..formatting import format_money
from ..routes import MAIN_MENU
from .standard import StandardScreen


class BankruptcyScreen(StandardScreen):
    """Game over screen shown when the player is bankrupt."""

    BINDINGS = [
        ("enter", "main_menu", "Main Menu"),
        ("up", "focus_prev", "Prev"),
        ("down", "focus_next", "Next"),
    ]

    TITLE = "Game Over: Bankruptcy"

    def compose_body(self) -> ComposeResult:
        """Build the bankruptcy layout."""

        with Vertical(classes="menu-button-group"):
            self.message = Static("", markup=True)
            self.main_menu_button = Button("Main Menu", id="main-menu", classes="menu-button")
            yield self.message
            yield self.main_menu_button

    def compose_actions(self) -> list[Button]:
        return []

    def on_mount(self) -> None:
        """Focus the main menu button."""

        super().on_mount()
        self.refresh_view()
        self.main_menu_button.focus()

    def refresh_view(self) -> None:
        """Update bankruptcy text."""

        show_index = self.app.state.show_index
        money = self.app.state.money
        self.message.update(
            "\n".join(
                [
                    "You cannot run a valid show with your current funds.",
                    "",
                    f"Final Show: #{show_index}",
                    f"Final Money: {format_money(money)}",
                ]
            )
        )

    def action_main_menu(self) -> None:
        """Return to the main menu."""

        self.app.navigate(MAIN_MENU)

    def action_focus_next(self) -> None:
        self.main_menu_button.focus()

    def action_focus_prev(self) -> None:
        self.main_menu_button.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "main-menu":
            self.action_main_menu()
