"""Base modal class for pygame UI modals."""

from typing import Callable, Optional
import pygame_gui
from pygame.rect import Rect
from pygame_gui.core import UIContainer
from pygame_gui.elements import UIPanel, UILabel


class BaseModal:
    """Base class for all modals.

    Provides common functionality for modal dialogs including:
    - Centered positioning on the parent screen
    - Container management for UI elements
    - Close callback handling
    """

    # Default modal dimensions (in design resolution units)
    DEFAULT_WIDTH = 360
    DEFAULT_HEIGHT = 200

    def __init__(
        self,
        app,
        manager: pygame_gui.UIManager,
        parent_rect: Rect,
        on_close: Optional[Callable[[], None]] = None,
    ) -> None:
        """Initialize the base modal.

        Args:
            app: The main application instance.
            manager: The pygame_gui UIManager instance.
            parent_rect: The parent screen rectangle for centering.
            on_close: Optional callback to invoke when modal closes.
        """
        self._app = app
        self._manager = manager
        self._parent_rect = parent_rect
        self._container: Optional[UIContainer] = None
        self._on_close = on_close
        self._title_label: Optional[UILabel] = None

    def _calculate_centered_rect(self, width: int = None, height: int = None) -> Rect:
        """Calculate the centered rectangle for the modal.

        Args:
            width: Modal width in pixels. Defaults to DEFAULT_WIDTH.
            height: Modal height in pixels. Defaults to DEFAULT_HEIGHT.

        Returns:
            A pygame.Rect positioned at the center of the parent.
        """
        width = width or self.DEFAULT_WIDTH
        height = height or self.DEFAULT_HEIGHT

        x = self._parent_rect.centerx - width // 2
        y = self._parent_rect.centery - height // 2

        return Rect(x, y, width, height)

    def show(self) -> None:
        """Create and display the modal container.

        Creates a centered panel container on the parent screen.
        Subclasses should override this to add their specific UI elements.
        """
        if self._container is not None:
            return

        modal_rect = self._calculate_centered_rect()

        # Create the modal panel container
        self._container = UIPanel(
            relative_rect=modal_rect,
            manager=self._manager,
            starting_layer_height=100,  # Ensure modal appears above other UI
        )

    def close(self) -> None:
        """Close the modal and invoke the on_close callback.

        Destroys the container and calls the optional on_close callback.
        """
        if self._container is not None:
            self._container.kill()
            self._container = None

        if self._on_close is not None:
            self._on_close()

    def is_open(self) -> bool:
        """Check if the modal is currently open.

        Returns:
            True if the modal container exists and is visible.
        """
        return self._container is not None

    def handle_event(self, event) -> bool:
        """Handle pygame events for the modal.

        Args:
            event: The pygame event to process.

        Returns:
            True if the event was consumed, False otherwise.
        """
        return False

    def update(self, time_delta: float) -> None:
        """Update the modal state each frame.

        Args:
            time_delta: Time elapsed since last frame in seconds.
        """
        pass
