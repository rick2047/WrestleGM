"""Visual snapshot tests for BookingHubScreen."""

import pytest
from pygame import Rect


def test_booking_hub_render(pygame_app, snapshot_image):
    """Test booking hub renders correctly."""
    app = pygame_app
    app.state.new_game()
    app.router.navigate("booking_hub")

    current = app.router.current
    if current:
        current.build(app.ui_manager, Rect(0, 0, 480, 800))

    app.ui_manager.update(0.016)
    assert current is not None


def test_booking_hub_empty_card(pygame_app, snapshot_image):
    """Test booking hub with empty show card."""
    pass


def test_booking_hub_partial_card(pygame_app, snapshot_image):
    """Test booking hub with partially booked card."""
    pass
