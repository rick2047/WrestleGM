"""Error modal for pygame UI."""

from typing import Callable, Optional
import pygame
import pygame_gui
from pygame.rect import Rect
from pygame_gui.elements import UILabel, UIButton

from .base import BaseModal


class ErrorModal(BaseModal):
    """Error message modal with OK button.

    Displays a modal dialog with an error title, message, and an OK button.
    Used for displaying errors like corrupt save data or save/load failures.
    """

    DEFAULT_WIDTH = 360
    DEFAULT_HEIGHT = 200

    def __init__(
        self,
        app,
        manager,
        parent_rect: Rect,
        title: str,
        message: str,
        on_ok: Optional[Callable[[], None]] = None,
        ok_text: str = "OK",
    ) -> None:
        """Initialize the error modal.

        Args:
            app: The main application instance.
            manager: The pygame_gui UIManager instance.
            parent_rect: The parent screen rectangle for centering.
            title: The error title to display.
            message: The error message to display.
            on_ok: Optional callback invoked when OK is clicked.
            ok_text: Text for the OK button. Defaults to "OK".
        """
        super().__init__(app, manager, parent_rect)
        self._title = title
        self._message = message
        self._on_ok = on_ok
        self._ok_text = ok_text
        self._ok_button: Optional[UIButton] = None
        self._title_label: Optional[UILabel] = None
        self._message_label: Optional[UILabel] = None

    def show(self) -> None:
        """Create and display the error modal."""
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
        message_rect = Rect(10, 50, modal_rect.width - 20, 70)
        self._message_label = UILabel(
            relative_rect=message_rect,
            text=self._message,
            manager=self._manager,
            container=self._container,
        )

        # Add OK button (centered at bottom)
        button_width = 100
        button_height = 40
        button_x = (modal_rect.width - button_width) // 2
        button_y = modal_rect.height - button_height - 20

        ok_rect = Rect(button_x, button_y, button_width, button_height)
        self._ok_button = UIButton(
            relative_rect=ok_rect,
            text=self._ok_text,
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
            if event.ui_element == self._ok_button:
                self.close()
                if self._on_ok:
                    self._on_ok()
                return True

        return False
