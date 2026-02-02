"""Roster screen with full roster inspection."""

from __future__ import annotations

import pygame_gui
from pygame.rect import Rect
from pygame_gui.elements import UIButton, UILabel, UIPanel, UIScrollingContainer

from .base import BaseScreen

if __name__ == "__main__":
    from ...ui_pygame.app import WrestleGMApp


class RosterScreen(BaseScreen):
    """Full roster inspection screen."""

    def __init__(self, app: WrestleGMApp, router) -> None:
        super().__init__(app, router)
        self._scroll_container = None
        self._back_button = None
        self._wrestler_panels: list[tuple] = []  # (panel, wrestler)

    def _build_header(self, manager, rect) -> None:
        """Build header with title and back button."""
        # Back button on left
        back_rect = Rect(rect.x + 8, rect.y + 10, 60, 30)
        self._back_button = UIButton(
            relative_rect=back_rect,
            text="BACK",
            manager=manager,
        )

        # Title
        title_rect = Rect(rect.x + 80, rect.y + 10, rect.width - 160, 30)
        UILabel(
            relative_rect=title_rect,
            text="ROSTER",
            manager=manager,
        )

        # Money display
        money_rect = Rect(rect.x + rect.width - 100, rect.y + 10, 90, 30)
        UILabel(
            relative_rect=money_rect,
            text=f"${self._app.state.money:,}",
            manager=manager,
        )

    def _build_body(self, manager, rect) -> None:
        """Build scrollable list of all wrestlers."""
        # Create scrolling container
        scroll_rect = Rect(rect.x + 8, rect.y + 8, rect.width - 16, rect.height - 16)
        self._scroll_container = UIScrollingContainer(
            relative_rect=scroll_rect,
            manager=manager,
        )

        # Build wrestler list
        self._wrestler_panels = []

        roster = list(self._app.state.roster.values())
        row_height = 60
        row_spacing = 4

        for i, wrestler in enumerate(roster):
            # Row panel (clickable)
            row_y = i * (row_height + row_spacing)
            row_rect = Rect(0, row_y, scroll_rect.width - 24, row_height)
            row_panel = UIPanel(
                relative_rect=row_rect,
                manager=manager,
                container=self._scroll_container,
            )

            # Avatar placeholder (32x32)
            avatar_rect = Rect(8, 14, 32, 32)
            avatar_text = wrestler.name[:2].upper() if wrestler.name else "??"
            UILabel(
                relative_rect=avatar_rect,
                text=avatar_text,
                manager=manager,
                container=row_panel,
            )

            # Name
            name_rect = Rect(48, 8, row_rect.width - 160, 20)
            UILabel(
                relative_rect=name_rect,
                text=wrestler.name[:20],
                manager=manager,
                container=row_panel,
            )

            # Stats line (Pop, Sta, Mic)
            stats_rect = Rect(48, 30, 120, 18)
            stats_text = (
                f"P:{wrestler.popularity} S:{wrestler.stamina} M:{wrestler.mic_skill}"
            )
            UILabel(
                relative_rect=stats_rect,
                text=stats_text,
                manager=manager,
                container=row_panel,
            )

            # Booking price
            cost = self._app.state.wrestler_booking_price(wrestler.id)
            cost_rect = Rect(row_rect.width - 110, 8, 100, 20)
            UILabel(
                relative_rect=cost_rect,
                text=f"${cost:,}",
                manager=manager,
                container=row_panel,
            )

            # Alignment
            align_rect = Rect(row_rect.width - 110, 30, 80, 18)
            align_text = "Face" if wrestler.alignment == "Face" else "Heel"
            UILabel(
                relative_rect=align_rect,
                text=align_text,
                manager=manager,
                container=row_panel,
            )

            # Store panel for click detection
            self._wrestler_panels.append((row_panel, wrestler))

        # Set scrollable area height
        total_height = len(roster) * (row_height + row_spacing)
        self._scroll_container.set_scrollable_area_dimensions(
            (scroll_rect.width - 24, total_height)
        )

    def _build_actions(self, manager, rect) -> None:
        """No action buttons for roster screen."""
        pass

    def _build_footer(self, manager, rect) -> None:
        """Build footer with hints."""
        footer_rect = Rect(rect.x + 8, rect.y + 8, rect.width - 16, 24)
        UILabel(
            relative_rect=footer_rect,
            text="Click on a wrestler to inspect details",
            manager=manager,
        )

    def _on_wrestler_clicked(self, wrestler) -> None:
        """Open the inspect modal for the selected wrestler."""
        from ..modals.inspect import WrestlerInspectModal

        # Build rivalry list for this wrestler
        rivalries = self._build_rivalry_list(wrestler.id)

        modal = WrestlerInspectModal(
            self._app,
            self._app._ui_manager,
            self._container.get_rect(),
            wrestler,
            rivalries,
        )
        modal.show()

    def _build_rivalry_list(self, wrestler_id: str) -> list[str]:
        """Build rivalry list entries for the inspected wrestler."""
        entries: list[str] = []
        for opponent_id, opponent in self._app.state.roster.items():
            if opponent_id == wrestler_id:
                continue
            emoji = self._app.state.rivalry_emoji_for_pair(wrestler_id, opponent_id)
            if emoji:
                entries.append(f"{emoji} {opponent.name}")
        return entries

    def _on_back_clicked(self) -> None:
        """Return to previous screen."""
        self._router.back()

    def handle_event(self, event) -> bool:
        """Handle pygame events for this screen."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # Check back button
            if event.ui_element == self._back_button:
                self._on_back_clicked()
                return True

        # Check for clicks on wrestler rows
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for panel, wrestler in self._wrestler_panels:
                # Check if the click came from this panel or its children
                if event.ui_element == panel or (
                    hasattr(event.ui_element, "get_container")
                    and event.ui_element.get_container() == panel
                ):
                    self._on_wrestler_clicked(wrestler)
                    return True

        return False
