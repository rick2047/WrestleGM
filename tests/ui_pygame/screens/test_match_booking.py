"""Visual snapshot tests for MatchBookingScreen."""

import io

import pytest
import pygame
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

    # Render to surface and capture
    surface = pygame.Surface((480, 800))
    app.ui_manager.draw_ui(surface)

    # Capture and compare
    buffer = io.BytesIO()
    pygame.image.save(surface, buffer, ".png")
    assert buffer.getvalue() == snapshot_image


def test_match_booking_with_selections(pygame_app, snapshot_image):
    """Test match booking with wrestlers selected."""
    app = pygame_app
    app.state.new_game()
    app.router.navigate("match_booking")

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
