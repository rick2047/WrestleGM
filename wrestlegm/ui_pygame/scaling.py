"""Scaling manager for UI scaling from design resolution to device."""

from pygame import Rect

from .constants import DESIGN_HEIGHT, DESIGN_WIDTH


class ScalingManager:
    """Manages UI scaling from design resolution to device."""

    def __init__(
        self, design_size: tuple[int, int], window_size: tuple[int, int]
    ) -> None:
        self._design = design_size
        self._window = window_size
        # Calculate scale (fit to smallest dimension)
        self._scale = min(
            window_size[0] / design_size[0], window_size[1] / design_size[1]
        )
        # Keep integer scale for pixel art
        self._ui_scale = max(1, int(self._scale))

    def scale(self, value: int) -> int:
        """Scale a design value to device pixels."""
        return int(value * self._scale)

    def ui_scale(self, value: int) -> int:
        """Scale for UI elements (integer only)."""
        return value * self._ui_scale

    def letterbox_rect(self) -> Rect:
        """Centered rect maintaining aspect ratio."""
        width = self.scale(DESIGN_WIDTH)
        height = self.scale(DESIGN_HEIGHT)
        x = (self._window[0] - width) // 2
        y = (self._window[1] - height) // 2
        return Rect(x, y, width, height)
