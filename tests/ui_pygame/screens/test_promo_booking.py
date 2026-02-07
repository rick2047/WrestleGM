"""Visual snapshot tests for PromoBookingScreen."""

import io

import pytest
import pygame
from pygame import Rect


def test_promo_booking_render(pygame_app, snapshot_image):
    """Test promo booking screen renders correctly."""
    app = pygame_app
    app._state = app.session.new_game(1, "Test Save")
    app.router.navigate("promo_booking")

    current = app.router.current
    if current:
        current.build(app.ui_manager, Rect(0, 0, 480, 800))

    app.ui_manager.update(0.016)

    # Render to surface and capture
    surface = pygame.Surface((480, 800))
    app.ui_manager.draw_ui(surface)

    # Capture and compare
    buffer = io.BytesIO()
    pygame.image.save(surface, buffer, ".png")
    assert buffer.getvalue() == snapshot_image
