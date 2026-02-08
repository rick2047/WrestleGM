"""Base screen with 4-zone layout (Header → Body → Actions → Footer)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..constants import HEADER_HEIGHT, ACTIONS_HEIGHT, FOOTER_HEIGHT

if TYPE_CHECKING:
    import pygame
    import pygame_gui


class BaseScreen:
    """Base screen with Header → Body → Actions → Footer layout.

    Subclasses override _build_header, _build_body, _build_actions, and _build_footer
    to define their UI elements.
    """

    def __init__(self, app, router) -> None:
        self._app = app
        self._router = router
        self._container = None

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

        # Zone heights imported from constants module

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
        """Build header UI elements.

        Override in subclasses to add:
        - Title label (left)
        - Info labels (center, right)
        """
        pass

    def _build_body(self, manager, rect) -> None:
        """Build body UI elements.

        Override in subclasses - scrollable content area.
        """
        pass

    def _build_actions(self, manager, rect) -> None:
        """Build actions UI elements.

        Override in subclasses for action buttons (horizontal layout).
        """
        pass

    def _build_footer(self, manager, rect) -> None:
        """Build footer UI elements.

        Override in subclasses for status/hints label.
        """
        pass

    def update(self, time_delta: float) -> None:
        """Called each frame to update animations/state.

        Override in subclasses for screen-specific updates.
        """
        pass

    def handle_event(self, event) -> bool:
        """Handle screen-specific events.

        Args:
            event: pygame event object

        Returns:
            True if the event was consumed, False otherwise
        """
        return False
