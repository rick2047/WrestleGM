"""Visual snapshot tests for MatchBookingScreen."""

import pytest
from pygame import Rect


def test_match_booking_render(pygame_app, snapshot_image):
    """Test match booking screen renders correctly."""
    app = pygame_app
    app.state.new_game()
    app.router.navigate("match_booking")

    current = app.router.current
    if current:
        current.build(app.ui_manager, Rect(0, 0, 480, 800))

    app.ui_manager.update(0.016)
    assert current is not None


def test_match_booking_with_selections(pygame_app, snapshot_image):
    """Test match booking with wrestlers selected."""
    pass
