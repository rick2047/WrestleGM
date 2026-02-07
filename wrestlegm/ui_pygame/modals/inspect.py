"""Wrestler inspect modal for detailed wrestler view."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from pygame.rect import Rect
from pygame_gui.elements import UIButton, UILabel

from .base import BaseModal

if TYPE_CHECKING:
    from wrestlegm.ui_pygame.app import WrestleGMApp


MAX_DESCRIPTION_LENGTH = 50
MAX_RIVALRIES_DISPLAY = 3


class WrestlerInspectModal(BaseModal):
    """Detailed wrestler information modal."""

    DEFAULT_WIDTH = 400
    DEFAULT_HEIGHT = 450

    def __init__(
        self,
        app: "WrestleGMApp",
        manager,
        parent_rect: Rect,
        wrestler,
        rivalries: Optional[list[str]] = None,
    ) -> None:
        super().__init__(app, manager, parent_rect)
        self._wrestler = wrestler
        self._rivalries = rivalries or []
        self._close_button: Optional[UIButton] = None
        self._name_label: Optional[UILabel] = None
        self._stats_label: Optional[UILabel] = None
        self._description_label: Optional[UILabel] = None
        self._rivalries_label: Optional[UILabel] = None
        self._avatar_label: Optional[UILabel] = None

    def show(self) -> None:
        """Create and display the modal with full wrestler details."""
        import pygame_gui

        if self._container is not None:
            return

        modal_rect = self._calculate_centered_rect(
            self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT
        )

        # Create the modal panel container
        self._container = pygame_gui.elements.UIPanel(
            relative_rect=modal_rect,
            manager=self._manager,
        )

        # Title
        title_rect = Rect(10, 10, modal_rect.width - 20, 30)
        UILabel(
            relative_rect=title_rect,
            text="Wrestler Details",
            manager=self._manager,
            container=self._container,
        )

        # Avatar (larger placeholder - 64x64 area)
        avatar_rect = Rect(
            (modal_rect.width - 64) // 2,
            50,
            64,
            64,
        )
        avatar_text = self._wrestler.name[:2].upper() if self._wrestler.name else "??"
        self._avatar_label = UILabel(
            relative_rect=avatar_rect,
            text=avatar_text,
            manager=self._manager,
            container=self._container,
        )

        # Name (bigger, below avatar)
        name_rect = Rect(10, 120, modal_rect.width - 20, 30)
        self._name_label = UILabel(
            relative_rect=name_rect,
            text=self._wrestler.name,
            manager=self._manager,
            container=self._container,
        )

        # Stats (Pop, Sta, Mic)
        stats_rect = Rect(10, 160, modal_rect.width - 20, 60)
        stats_text = (
            f"Popularity: {self._wrestler.popularity}  |  "
            f"Stamina: {self._wrestler.stamina}  |  "
            f"Mic Skill: {self._wrestler.mic_skill}"
        )
        self._stats_label = UILabel(
            relative_rect=stats_rect,
            text=stats_text,
            manager=self._manager,
            container=self._container,
        )

        # Alignment
        alignment_rect = Rect(10, 230, modal_rect.width - 20, 25)
        alignment_text = f"Alignment: {self._wrestler.alignment}"
        UILabel(
            relative_rect=alignment_rect,
            text=alignment_text,
            manager=self._manager,
            container=self._container,
        )

        # Description (if available)
        y_offset = 265
        description = getattr(self._wrestler, "description", "")
        if description:
            desc_rect = Rect(10, y_offset, modal_rect.width - 20, 40)
            # Truncate if too long
            if len(description) > MAX_DESCRIPTION_LENGTH:
                description = description[: MAX_DESCRIPTION_LENGTH - 3] + "..."
            self._description_label = UILabel(
                relative_rect=desc_rect,
                text=description,
                manager=self._manager,
                container=self._container,
            )
            y_offset += 50

        # Active rivalries
        if self._rivalries:
            rivalries_rect = Rect(10, y_offset, modal_rect.width - 20, 25)
            self._rivalries_label = UILabel(
                relative_rect=rivalries_rect,
                text="Active Rivalries:",
                manager=self._manager,
                container=self._container,
            )
            y_offset += 30

            # List rivalries (max lines)
            for i, rivalry in enumerate(self._rivalries[:MAX_RIVALRIES_DISPLAY]):
                rivalry_rect = Rect(20, y_offset, modal_rect.width - 40, 20)
                UILabel(
                    relative_rect=rivalry_rect,
                    text=f"  • {rivalry}",
                    manager=self._manager,
                    container=self._container,
                )
                y_offset += 22

        # Close button at bottom
        button_width = 100
        button_height = 40
        close_rect = Rect(
            (modal_rect.width - button_width) // 2,
            modal_rect.height - button_height - 15,
            button_width,
            button_height,
        )
        self._close_button = UIButton(
            relative_rect=close_rect,
            text="CLOSE",
            manager=self._manager,
            container=self._container,
        )

    def handle_event(self, event) -> bool:
        """Handle pygame events."""
        import pygame_gui

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self._close_button:
                self.close()
                return True
        return False
