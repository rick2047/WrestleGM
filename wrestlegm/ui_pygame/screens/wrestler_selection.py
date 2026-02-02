"""Wrestler selection screen with scrollable roster list."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import pygame_gui
from pygame.rect import Rect
from pygame_gui.elements import UIButton, UILabel, UIPanel, UIScrollingContainer

if TYPE_CHECKING:
    pass


class WrestlerSelectionScreen:
    """Scrollable list of available wrestlers."""

    def __init__(
        self,
        app,
        router,
        on_select: Callable | None = None,
        exclude: list[str] | None = None,
        slot_index: int = 0,
    ):
        self._app = app
        self._router = router
        self._on_select = on_select
        self._exclude = exclude or []
        self._slot_index = slot_index
        self._container = None
        self._scroll_container = None
        self._wrestler_buttons: list[UIButton] = []
        self._wrestler_data: list[tuple] = []
        self._back_button: UIButton | None = None

    def build(self, manager, rect) -> None:
        """Build UI elements in the 4 zones."""
        zones = self._compute_zones(rect)
        self._build_header(manager, zones["header"])
        self._build_body(manager, zones["body"])
        self._build_actions(manager, zones["actions"])
        self._build_footer(manager, zones["footer"])

    def _compute_zones(self, rect):
        """Calculate header, body, actions, footer rectangles."""
        from pygame import Rect

        HEADER_HEIGHT = 50
        ACTIONS_HEIGHT = 70
        FOOTER_HEIGHT = 40

        x = rect.x
        y = rect.y
        width = rect.width

        header_rect = Rect(x, y, width, HEADER_HEIGHT)
        body_y = y + HEADER_HEIGHT
        body_height = rect.height - HEADER_HEIGHT - ACTIONS_HEIGHT - FOOTER_HEIGHT
        body_rect = Rect(x, body_y, width, body_height)
        actions_y = body_y + body_height
        actions_rect = Rect(x, actions_y, width, ACTIONS_HEIGHT)
        footer_y = actions_y + ACTIONS_HEIGHT
        footer_rect = Rect(x, footer_y, width, FOOTER_HEIGHT)

        return {
            "header": header_rect,
            "body": body_rect,
            "actions": actions_rect,
            "footer": footer_rect,
        }

    def _build_header(self, manager, rect) -> None:
        """Build header with title and back button."""
        # Title
        title_rect = Rect(rect.x + 8, rect.y + 10, rect.width - 80, 30)
        UILabel(
            relative_rect=title_rect,
            text="SELECT WRESTLER",
            manager=manager,
        )

        # Money display
        money_rect = Rect(rect.x + rect.width - 120, rect.y + 10, 110, 30)
        UILabel(
            relative_rect=money_rect,
            text=f"${self._app.state.money:,}",
            manager=manager,
        )

    def _build_body(self, manager, rect) -> None:
        """Build scrollable list of wrestlers."""
        # Create scrolling container
        scroll_rect = Rect(rect.x + 8, rect.y + 8, rect.width - 16, rect.height - 16)
        self._scroll_container = UIScrollingContainer(
            relative_rect=scroll_rect,
            manager=manager,
        )

        # Build wrestler list
        self._wrestler_buttons = []
        self._wrestler_data = []

        roster = list(self._app.state.roster.values())
        row_height = 60
        row_spacing = 4

        for i, wrestler in enumerate(roster):
            is_available = self._is_wrestler_available(wrestler)
            unavailable_reason = self._get_unavailable_reason(wrestler)

            # Row panel
            row_y = i * (row_height + row_spacing)
            row_rect = Rect(0, row_y, scroll_rect.width - 24, row_height)
            row_panel = UIPanel(
                relative_rect=row_rect,
                manager=manager,
                container=self._scroll_container,
            )

            # Avatar placeholder (32x32)
            avatar_rect = Rect(8, 14, 32, 32)
            UILabel(
                relative_rect=avatar_rect,
                text="👤",
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

            # Cost
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

            # Unavailable reason label (if unavailable)
            if not is_available:
                reason_rect = Rect(170, 30, 100, 18)
                UILabel(
                    relative_rect=reason_rect,
                    text=unavailable_reason,
                    manager=manager,
                    container=row_panel,
                )
                # Gray out the row visually by disabling interactions
                row_panel.disable()
            else:
                # Select button
                select_rect = Rect(row_rect.width - 50, 14, 44, 32)
                select_button = UIButton(
                    relative_rect=select_rect,
                    text="+",
                    manager=manager,
                    container=row_panel,
                )
                self._wrestler_buttons.append(select_button)
                self._wrestler_data.append(wrestler)

        # Set scrollable area height
        total_height = len(roster) * (row_height + row_spacing)
        self._scroll_container.set_scrollable_area_dimensions(
            (scroll_rect.width - 24, total_height)
        )

    def _build_actions(self, manager, rect) -> None:
        """Build action buttons."""
        button_width = 120
        button_height = 44
        button_y = rect.y + (rect.height - button_height) // 2

        # Cancel/Back button
        cancel_rect = Rect(
            rect.x + (rect.width - button_width) // 2,
            button_y,
            button_width,
            button_height,
        )
        self._back_button = UIButton(
            relative_rect=cancel_rect,
            text="BACK",
            manager=manager,
        )

    def _build_footer(self, manager, rect) -> None:
        """Build footer with hints."""
        footer_rect = Rect(rect.x + 8, rect.y + 8, rect.width - 16, 24)
        UILabel(
            relative_rect=footer_rect,
            text="Click + to select a wrestler",
            manager=manager,
        )

    def _is_wrestler_available(self, wrestler) -> bool:
        """Check if a wrestler can be selected."""
        # Check if in exclude list (already selected in this match)
        if wrestler.id in self._exclude:
            return False

        # Check if already booked in another slot
        if self._app.state.is_wrestler_booked(
            wrestler.id, exclude_slot=self._slot_index
        ):
            return False

        # Check stamina
        from wrestlegm import constants

        if wrestler.stamina <= constants.STAMINA_MIN_BOOKABLE:
            return False

        return True

    def _get_unavailable_reason(self, wrestler) -> str:
        """Get the reason why a wrestler is unavailable."""
        from wrestlegm import constants

        if wrestler.id in self._exclude:
            return "Selected"

        if self._app.state.is_wrestler_booked(
            wrestler.id, exclude_slot=self._slot_index
        ):
            return "Booked"

        if wrestler.stamina <= constants.STAMINA_MIN_BOOKABLE:
            return "Low Stamina"

        return ""

    def _on_wrestler_clicked(self, wrestler) -> None:
        """Handle wrestler selection."""
        if not self._is_wrestler_available(wrestler):
            return

        if self._on_select:
            self._on_select(wrestler)

        self._router.back()

    def _on_back_clicked(self) -> None:
        """Return to previous screen without selection."""
        self._router.back()

    def handle_event(self, event) -> bool:
        """Handle pygame events for this screen."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # Check wrestler selection buttons
            for i, button in enumerate(self._wrestler_buttons):
                if event.ui_element == button:
                    wrestler = self._wrestler_data[i]
                    self._on_wrestler_clicked(wrestler)
                    return True

            # Check back button
            if event.ui_element == self._back_button:
                self._on_back_clicked()
                return True

        return False

    def update(self, time_delta: float) -> None:
        """Update screen state."""
        pass
