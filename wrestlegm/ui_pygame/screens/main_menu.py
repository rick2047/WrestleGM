"""Main menu screen for WrestleGM pygame UI."""

from __future__ import annotations

import pygame
import pygame_gui
from pygame.rect import Rect
from pygame_gui.elements import UIButton, UILabel

from .base import BaseScreen


class MainMenuScreen(BaseScreen):
    """Main menu with New Game, Load Game, Quit options."""

    def __init__(self, app, router) -> None:
        super().__init__(app, router)
        self._new_game_button: pygame_gui.elements.UIButton | None = None
        self._load_game_button: pygame_gui.elements.UIButton | None = None
        self._quit_button: pygame_gui.elements.UIButton | None = None

    def _build_header(self, manager, rect) -> None:
        """Build header with title."""
        # Title label centered in header
        title_rect = Rect(rect.x, rect.y + 10, rect.width, 30)
        UILabel(
            relative_rect=title_rect,
            text="WRESTLE GM",
            manager=manager,
        )

    def _build_body(self, manager, rect) -> None:
        """Build body with menu buttons centered vertically."""
        from ..constants import MARGIN, PADDING

        # Button dimensions
        button_width = 200
        button_height = 60
        button_gap = 20

        # Calculate total height of button group
        total_height = (button_height * 3) + (button_gap * 2)

        # Center the buttons vertically in the body
        start_y = rect.y + (rect.height - total_height) // 2
        center_x = rect.x + rect.width // 2

        # Create New Game button
        new_game_rect = Rect(
            center_x - button_width // 2,
            start_y,
            button_width,
            button_height,
        )
        self._new_game_button = UIButton(
            relative_rect=new_game_rect,
            text="NEW GAME",
            manager=manager,
        )

        # Create Load Game button
        load_game_rect = Rect(
            center_x - button_width // 2,
            start_y + button_height + button_gap,
            button_width,
            button_height,
        )
        self._load_game_button = UIButton(
            relative_rect=load_game_rect,
            text="LOAD GAME",
            manager=manager,
        )

        # Create Quit button
        quit_rect = Rect(
            center_x - button_width // 2,
            start_y + (button_height + button_gap) * 2,
            button_width,
            button_height,
        )
        self._quit_button = UIButton(
            relative_rect=quit_rect,
            text="QUIT",
            manager=manager,
        )

    def _build_actions(self, manager, rect) -> None:
        """No action buttons needed for main menu."""
        pass

    def _build_footer(self, manager, rect) -> None:
        """Build footer with hint text."""
        hint_rect = Rect(rect.x, rect.y + 10, rect.width, 20)
        UILabel(
            relative_rect=hint_rect,
            text="Select an option to continue",
            manager=manager,
        )

    def handle_event(self, event) -> bool:
        """Handle button press events."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self._new_game_button:
                self._on_new_game()
                return True
            elif event.ui_element == self._load_game_button:
                self._on_load_game()
                return True
            elif event.ui_element == self._quit_button:
                self._on_quit()
                return True
        return False

    def _on_new_game(self) -> None:
        """Navigate to save slots in new game mode."""
        self._router.navigate("save_slots", mode="new")

    def _on_load_game(self) -> None:
        """Navigate to save slots in load game mode."""
        self._router.navigate("save_slots", mode="load")

    def _on_quit(self) -> None:
        """Quit the application."""
        self._app.quit()
