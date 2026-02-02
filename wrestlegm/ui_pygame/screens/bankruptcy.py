"""Bankruptcy game over screen with restart options."""

from __future__ import annotations

import pygame_gui
from pygame.rect import Rect
from pygame_gui.elements import UIButton, UILabel, UIPanel

from .base import BaseScreen


class BankruptcyScreen(BaseScreen):
    """Displayed when promotion runs out of money."""

    def __init__(self, app, router) -> None:
        super().__init__(app, router)
        self._try_again_button = None
        self._main_menu_button = None

    def _build_header(self, manager, rect) -> None:
        """Build header with danger-colored title."""
        # Title in red/danger color
        title_rect = Rect(rect.x + 8, rect.y + 10, rect.width - 16, 30)
        UILabel(
            relative_rect=title_rect,
            text="BANKRUPTCY",
            manager=manager,
        )

    def _build_body(self, manager, rect) -> None:
        """Build bankruptcy message and stats display."""
        from ..constants import COLOR_DANGER

        # Center panel for content
        panel_width = rect.width - 32
        panel_height = rect.height - 32
        panel_x = rect.x + 16
        panel_y = rect.y + 16

        content_panel = UIPanel(
            relative_rect=Rect(panel_x, panel_y, panel_width, panel_height),
            manager=manager,
        )

        # "BANKRUPT!" message (large)
        bankrupt_rect = Rect(20, 20, panel_width - 40, 50)
        # Create a visual representation of danger text
        UILabel(
            relative_rect=bankrupt_rect,
            text="BANKRUPT!",
            manager=manager,
            container=content_panel,
        )

        # Subtitle message
        message_rect = Rect(20, 80, panel_width - 40, 30)
        UILabel(
            relative_rect=message_rect,
            text="Your promotion has run out of funds.",
            manager=manager,
            container=content_panel,
        )

        # Show final stats
        show_index = self._app.state.show_index
        money = self._app.state.money

        stats_y = 130
        stats_spacing = 30

        show_rect = Rect(20, stats_y, panel_width - 40, 25)
        UILabel(
            relative_rect=show_rect,
            text=f"Final Show: #{show_index}",
            manager=manager,
            container=content_panel,
        )

        money_rect = Rect(20, stats_y + stats_spacing, panel_width - 40, 25)
        UILabel(
            relative_rect=money_rect,
            text=f"Final Money: ${money:,}",
            manager=manager,
            container=content_panel,
        )

    def _build_actions(self, manager, rect) -> None:
        """Build Try Again and Main Menu buttons."""
        button_width = 140
        button_height = 44
        button_y = rect.y + (rect.height - button_height) // 2

        # Try Again button (left)
        try_rect = Rect(
            rect.x + (rect.width // 2) - button_width - 10,
            button_y,
            button_width,
            button_height,
        )
        self._try_again_button = UIButton(
            relative_rect=try_rect,
            text="TRY AGAIN",
            manager=manager,
        )

        # Main Menu button (right)
        menu_rect = Rect(
            rect.x + (rect.width // 2) + 10, button_y, button_width, button_height
        )
        self._main_menu_button = UIButton(
            relative_rect=menu_rect,
            text="MAIN MENU",
            manager=manager,
        )

    def _build_footer(self, manager, rect) -> None:
        """Build footer with hint."""
        footer_rect = Rect(rect.x + 8, rect.y + 8, rect.width - 16, 24)
        UILabel(
            relative_rect=footer_rect,
            text="Game Over - Choose an option to continue",
            manager=manager,
        )

    def _on_try_again(self) -> None:
        """Reset game state and navigate to booking hub."""
        self._app.state.reset_to_initial()
        self._router.navigate("booking_hub")

    def _on_main_menu(self) -> None:
        """Navigate to main menu."""
        self._router.navigate("main_menu")

    def handle_event(self, event) -> bool:
        """Handle pygame events for this screen."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self._try_again_button:
                self._on_try_again()
                return True
            elif event.ui_element == self._main_menu_button:
                self._on_main_menu()
                return True

        return False
