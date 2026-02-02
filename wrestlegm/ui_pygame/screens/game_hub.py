"""Game hub screen for an active session."""

from __future__ import annotations

from pygame.rect import Rect
from pygame_gui.elements import UIButton, UILabel

from wrestlegm.ui_pygame.screens.base import BaseScreen
from wrestlegm.ui_pygame.constants import (
    MARGIN,
    PADDING,
    FONT_SIZE_HEADER,
    FONT_SIZE_BODY,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
)


class GameHubScreen(BaseScreen):
    """Central game hub with navigation options.

    Responsibilities:
    - Present session-aware navigation into gameplay screens.
    - Display the current show number.
    - Allow save and exit back to the main menu.
    """

    def __init__(self, app, router) -> None:
        super().__init__(app, router)
        self._title_label: UILabel | None = None
        self._money_label: UILabel | None = None
        self._continue_button: UIButton | None = None
        self._booking_button: UIButton | None = None
        self._roster_button: UIButton | None = None
        self._save_quit_button: UIButton | None = None

    def _build_header(self, manager, rect: Rect) -> None:
        """Build header with title and money display."""
        # Title on the left
        title_rect = Rect(
            rect.x + MARGIN,
            rect.y + PADDING,
            rect.width // 2 - MARGIN * 2,
            rect.height - PADDING * 2,
        )
        self._title_label = UILabel(
            relative_rect=title_rect,
            text="GAME HUB",
            manager=manager,
        )

        # Money on the right
        money_text = self._format_money(self._app.state.money)
        money_rect = Rect(
            rect.x + rect.width // 2,
            rect.y + PADDING,
            rect.width // 2 - MARGIN * 2,
            rect.height - PADDING * 2,
        )
        self._money_label = UILabel(
            relative_rect=money_rect,
            text=money_text,
            manager=manager,
        )

    def _build_body(self, manager, rect: Rect) -> None:
        """Build body with four navigation buttons."""
        button_height = 60
        button_spacing = 16
        total_height = 4 * button_height + 3 * button_spacing
        start_y = rect.y + (rect.height - total_height) // 2

        # Continue Game button
        continue_rect = Rect(
            rect.x + MARGIN * 2,
            start_y,
            rect.width - MARGIN * 4,
            button_height,
        )
        show_num = self._app.state.show_index
        self._continue_button = UIButton(
            relative_rect=continue_rect,
            text=f"CONTINUE GAME\nShow #{show_num}",
            manager=manager,
        )

        # Booking Hub button
        booking_rect = Rect(
            rect.x + MARGIN * 2,
            start_y + button_height + button_spacing,
            rect.width - MARGIN * 4,
            button_height,
        )
        self._booking_button = UIButton(
            relative_rect=booking_rect,
            text="BOOKING HUB",
            manager=manager,
        )

        # Roster View button (placeholder)
        roster_rect = Rect(
            rect.x + MARGIN * 2,
            start_y + 2 * (button_height + button_spacing),
            rect.width - MARGIN * 4,
            button_height,
        )
        self._roster_button = UIButton(
            relative_rect=roster_rect,
            text="ROSTER VIEW\n(Coming Soon)",
            manager=manager,
        )

        # Save & Quit button
        save_quit_rect = Rect(
            rect.x + MARGIN * 2,
            start_y + 3 * (button_height + button_spacing),
            rect.width - MARGIN * 4,
            button_height,
        )
        self._save_quit_button = UIButton(
            relative_rect=save_quit_rect,
            text="SAVE & QUIT",
            manager=manager,
        )

    def _build_actions(self, manager, rect: Rect) -> None:
        """No action buttons needed - actions are in body."""
        pass

    def _build_footer(self, manager, rect: Rect) -> None:
        """Build footer with hint text."""
        footer_rect = Rect(
            rect.x + MARGIN,
            rect.y,
            rect.width - MARGIN * 2,
            rect.height,
        )
        UILabel(
            relative_rect=footer_rect,
            text="Select an option to continue",
            manager=manager,
        )

    def update(self, time_delta: float) -> None:
        """Update the money display."""
        if self._money_label:
            money_text = self._format_money(self._app.state.money)
            self._money_label.set_text(money_text)

    def handle_event(self, event) -> bool:
        """Handle button presses."""
        import pygame_gui

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self._continue_button:
                self._on_continue()
                return True
            elif event.ui_element == self._booking_button:
                self._on_booking_hub()
                return True
            elif event.ui_element == self._roster_button:
                self._on_roster()
                return True
            elif event.ui_element == self._save_quit_button:
                self._on_save_quit()
                return True

        return False

    def _on_continue(self) -> None:
        """Navigate to booking hub."""
        # Check for bankruptcy before going to booking
        if self._app.state.is_bankrupt():
            self._router.navigate("bankruptcy")
        else:
            self._router.navigate("booking_hub")

    def _on_booking_hub(self) -> None:
        """Navigate to booking hub."""
        # Check for bankruptcy before going to booking
        if self._app.state.is_bankrupt():
            self._router.navigate("bankruptcy")
        else:
            self._router.navigate("booking_hub")

    def _on_roster(self) -> None:
        """Navigate to roster screen (placeholder)."""
        # Roster screen not yet implemented
        pass

    def _on_save_quit(self) -> None:
        """Save game and return to main menu."""
        # Save using SessionManager
        if hasattr(self._app, "session") and self._app.session:
            self._app.session.save_current_slot(self._app.state)

        # Navigate back to main menu
        self._router.switch("main_menu")

    def _format_money(self, amount: int) -> str:
        """Format money for display."""
        if amount < 0:
            return f"-${abs(amount):,}"
        return f"${amount:,}"
