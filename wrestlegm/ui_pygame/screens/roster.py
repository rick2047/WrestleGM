"""Roster screen with full roster inspection."""

from __future__ import annotations

import pygame_gui
from pygame.rect import Rect
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIButton, UILabel, UIScrollingContainer

from wrestlegm.ui_pygame.wrestler_card import WrestlerCard

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
        self._wrestler_cards: list[WrestlerCard] = []

    def _build_header(self, manager, rect) -> None:
        """Build header with title and back button."""
        # Back button on left
        back_rect = Rect(rect.x + 8, rect.y + 10, 60, 30)
        self._back_button = UIButton(
            relative_rect=back_rect,
            text="BACK",
            manager=manager,
            object_id=ObjectID(
                class_id="@secondary_button", object_id="#roster_back_button"
            ),
        )

        # Title
        title_rect = Rect(rect.x + 80, rect.y + 10, rect.width - 160, 30)
        UILabel(
            relative_rect=title_rect,
            text="ROSTER",
            manager=manager,
            object_id=ObjectID(class_id="@header_title", object_id="#roster_title"),
        )

        # Money display
        money_rect = Rect(rect.x + rect.width - 100, rect.y + 10, 90, 30)
        UILabel(
            relative_rect=money_rect,
            text=f"${self._app.state.money:,}",
            manager=manager,
            object_id=ObjectID(class_id="@money_label", object_id="#roster_money"),
        )

    def _build_body(self, manager, rect) -> None:
        """Build scrollable list of all wrestlers."""
        # Create scrolling container
        scroll_rect = Rect(rect.x + 8, rect.y + 8, rect.width - 16, rect.height - 16)
        self._scroll_container = UIScrollingContainer(
            relative_rect=scroll_rect,
            manager=manager,
            object_id=ObjectID(class_id="@roster_scroll", object_id="#roster_scroll"),
        )

        # Build wrestler list
        self._wrestler_panels = []
        self._wrestler_cards = []

        roster = list(self._app.state.roster.values())
        row_height = 98
        row_spacing = 8

        for i, wrestler in enumerate(roster):
            row_y = i * (row_height + row_spacing)
            row_rect = Rect(0, row_y, scroll_rect.width - 24, row_height)
            cost = self._app.state.wrestler_booking_price(wrestler.id)
            definition = self._app.state.wrestler_defs.get(wrestler.id)
            avatar_path = definition.avatar_path if definition else ""
            card = WrestlerCard(
                row_rect,
                manager=manager,
                container=self._scroll_container,
                wrestler=wrestler,
                cost_text=f"${cost:,}",
                action_text="INSPECT",
                action_object_id="@secondary_button",
                avatar_path=avatar_path,
            )
            card.set_visible_fields({"name", "stats", "alignment", "cost", "action"})
            self._wrestler_cards.append(card)
            self._wrestler_panels.append((card.action_button, wrestler))

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
            object_id=ObjectID(class_id="@footer_hint", object_id="#roster_hint"),
        )

    def _on_wrestler_clicked(self, wrestler) -> None:
        """Open wrestler details using a Router-managed modal."""

        # Build rivalry list for this wrestler
        rivalries = self._build_rivalry_list(wrestler.id)
        rivalry_text = "\n".join(rivalries) if rivalries else "No active rivalries"

        details = (
            f"Popularity: {wrestler.popularity}\n"
            f"Stamina: {wrestler.stamina}\n"
            f"Mic Skill: {wrestler.mic_skill}\n"
            f"Alignment: {wrestler.alignment.title()}\n"
            f"\nRivalries:\n{rivalry_text}"
        )

        self._router.show_error(f"{wrestler.name}", details)

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

            # Check for clicks on wrestler row buttons
            for button, wrestler in self._wrestler_panels:
                if event.ui_element == button:
                    self._on_wrestler_clicked(wrestler)
                    return True

        return False
