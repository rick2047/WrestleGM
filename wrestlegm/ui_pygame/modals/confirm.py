"""Confirmation modal for pygame UI."""

from typing import Callable, Optional
import pygame
import pygame_gui
from pygame.rect import Rect
from pygame_gui.elements import UILabel, UIButton

from .base import BaseModal


class ConfirmModal(BaseModal):
    """Yes/No confirmation modal.

    Displays a modal dialog with a title, message, and Yes/No buttons.
    Used for confirming actions like running a show with debt or clearing a slot.
    """

    DEFAULT_WIDTH = 360
    DEFAULT_HEIGHT = 220

    def __init__(
        self,
        app,
        manager,
        parent_rect: Rect,
        title: str,
        message: str,
        on_confirm: Optional[Callable[[], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None,
        confirm_text: str = "Yes",
        cancel_text: str = "No",
    ) -> None:
        """Initialize the confirmation modal.

        Args:
            app: The main application instance.
            manager: The pygame_gui UIManager instance.
            parent_rect: The parent screen rectangle for centering.
            title: The modal title to display.
            message: The confirmation message to display.
            on_confirm: Optional callback invoked when Yes is clicked.
            on_cancel: Optional callback invoked when No is clicked.
            confirm_text: Text for the confirm button. Defaults to "Yes".
            cancel_text: Text for the cancel button. Defaults to "No".
        """
        super().__init__(app, manager, parent_rect)
        self._title = title
        self._message = message
        self._on_confirm = on_confirm
        self._on_cancel = on_cancel
        self._confirm_text = confirm_text
        self._cancel_text = cancel_text
        self._confirm_button: Optional[UIButton] = None
        self._cancel_button: Optional[UIButton] = None
        self._title_label: Optional[UILabel] = None
        self._message_label: Optional[UILabel] = None

    def show(self) -> None:
        """Create and display the confirmation modal."""
        if self._container is not None:
            return

        modal_rect = self._calculate_centered_rect(
            self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT
        )

        # Create the modal panel container
        from pygame_gui.elements import UIPanel

        self._container = UIPanel(
            relative_rect=modal_rect, manager=self._manager, starting_layer_height=100
        )

        # Add title label
        title_rect = Rect(10, 10, modal_rect.width - 20, 30)
        self._title_label = UILabel(
            relative_rect=title_rect,
            text=self._title,
            manager=self._manager,
            container=self._container,
        )

        # Add message label
        message_rect = Rect(10, 50, modal_rect.width - 20, 80)
        self._message_label = UILabel(
            relative_rect=message_rect,
            text=self._message,
            manager=self._manager,
            container=self._container,
        )

        # Add buttons
        button_width = 100
        button_height = 40
        button_y = modal_rect.height - button_height - 20

        # Cancel/No button (left)
        cancel_rect = Rect(40, button_y, button_width, button_height)
        self._cancel_button = UIButton(
            relative_rect=cancel_rect,
            text=self._cancel_text,
            manager=self._manager,
            container=self._container,
        )

        # Confirm/Yes button (right)
        confirm_rect = Rect(
            modal_rect.width - button_width - 40, button_y, button_width, button_height
        )
        self._confirm_button = UIButton(
            relative_rect=confirm_rect,
            text=self._confirm_text,
            manager=self._manager,
            container=self._container,
        )

    def handle_event(self, event) -> bool:
        """Handle pygame events for the modal.

        Args:
            event: The pygame event to process.

        Returns:
            True if the event was consumed, False otherwise.
        """
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self._confirm_button:
                self.close()
                if self._on_confirm:
                    self._on_confirm()
                return True
            elif event.ui_element == self._cancel_button:
                self.close()
                if self._on_cancel:
                    self._on_cancel()
                return True

        return False
