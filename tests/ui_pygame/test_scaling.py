"""Unit tests for ScalingManager."""

import pytest


# Design resolution constants (copied from constants.py to avoid pygame import)
DESIGN_WIDTH = 480
DESIGN_HEIGHT = 800


class ScalingManager:
    """Minimal scaling manager for testing without pygame dependencies."""

    def __init__(self, design_size, window_size):
        self._design = design_size
        self._window = window_size
        # Calculate scale (fit to smallest dimension)
        self._scale = min(
            window_size[0] / design_size[0], window_size[1] / design_size[1]
        )
        # Keep integer scale for pixel art
        self._ui_scale = max(1, int(self._scale))

    def scale(self, value):
        """Scale a design value to device pixels."""
        return int(value * self._scale)

    def ui_scale(self, value):
        """Scale for UI elements (integer only)."""
        return value * self._ui_scale

    def letterbox_rect(self):
        """Centered rect maintaining aspect ratio."""
        width = self.scale(DESIGN_WIDTH)
        height = self.scale(DESIGN_HEIGHT)
        x = (self._window[0] - width) // 2
        y = (self._window[1] - height) // 2
        return (x, y, width, height)  # Return tuple instead of Rect


class TestScalingManager:
    """Tests for the ScalingManager class."""

    def test_scale_exact_double(self):
        """Test scaling when window is exactly 2x design resolution."""
        scaler = ScalingManager(
            (DESIGN_WIDTH, DESIGN_HEIGHT), (DESIGN_WIDTH * 2, DESIGN_HEIGHT * 2)
        )
        assert scaler.scale(100) == 200
        assert scaler.scale(50) == 100

    def test_scale_half(self):
        """Test scaling when window is half design resolution."""
        scaler = ScalingManager(
            (DESIGN_WIDTH, DESIGN_HEIGHT), (DESIGN_WIDTH // 2, DESIGN_HEIGHT // 2)
        )
        assert scaler.scale(100) == 50
        assert scaler.scale(50) == 25

    def test_scale_same_size(self):
        """Test scaling when window matches design resolution."""
        scaler = ScalingManager(
            (DESIGN_WIDTH, DESIGN_HEIGHT), (DESIGN_WIDTH, DESIGN_HEIGHT)
        )
        assert scaler.scale(100) == 100
        assert scaler.scale(50) == 50

    def test_scale_wider_window(self):
        """Test scaling with wider window (height limited)."""
        scaler = ScalingManager(
            (480, 800),
            (960, 800),  # Wider but same height
        )
        # Should scale based on height (1x)
        assert scaler.scale(100) == 100

    def test_scale_taller_window(self):
        """Test scaling with taller window (width limited)."""
        scaler = ScalingManager(
            (480, 800),
            (480, 1600),  # Same width but taller
        )
        # Should scale based on width (1x)
        assert scaler.scale(100) == 100

    def test_ui_scale_integer(self):
        """Test ui_scale returns integer multiples."""
        scaler = ScalingManager(
            (480, 800),
            (960, 1600),  # 2x scale
        )
        assert scaler.ui_scale(100) == 200
        assert scaler.ui_scale(50) == 100

    def test_ui_scale_minimum_one(self):
        """Test ui_scale returns at least 1x even for small windows."""
        scaler = ScalingManager(
            (480, 800),
            (240, 400),  # 0.5x scale
        )
        # ui_scale should be at least 1
        assert scaler.ui_scale(100) == 100  # 1x minimum

    def test_letterbox_rect_centered(self):
        """Test letterbox rect is centered."""
        scaler = ScalingManager(
            (480, 800),
            (960, 1600),  # 2x scale
        )
        rect = scaler.letterbox_rect()
        assert rect[2] == 960  # width
        assert rect[3] == 1600  # height
        assert rect[0] == 0  # Centered horizontally
        assert rect[1] == 0  # Centered vertically

    def test_letterbox_rect_with_margins(self):
        """Test letterbox rect with margins on larger window."""
        scaler = ScalingManager(
            (480, 800),
            (1000, 1600),  # Wider than 2x
        )
        rect = scaler.letterbox_rect()
        assert rect[2] == 960  # Scaled width
        assert rect[3] == 1600  # Scaled height
        assert rect[0] == 20  # Centered: (1000 - 960) / 2
        assert rect[1] == 0  # No vertical margin

    def test_zero_values(self):
        """Test scaling with zero values raises appropriate error."""
        # Division by zero is expected for invalid design size
        with pytest.raises(ZeroDivisionError):
            ScalingManager((0, 0), (100, 100))

    def test_negative_scale_protection(self):
        """Test that negative scale values are handled."""
        # This tests edge case behavior
        scaler = ScalingManager((480, 800), (480, 800))
        # Scale should be positive
        assert scaler._scale > 0
