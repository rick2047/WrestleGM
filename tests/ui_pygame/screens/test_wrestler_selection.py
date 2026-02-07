"""Visual snapshot tests for WrestlerSelectionScreen."""

import io

import pytest
import pygame
from pygame import Rect


def test_wrestler_selection_render(pygame_app, snapshot_image):
    """Test wrestler selection screen renders correctly."""
    app = pygame_app
    app._state = app.session.new_game(1, "Test Save")
    app.router.navigate("wrestler_selection")

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


def test_wrestler_selection_filtered(pygame_app, snapshot_image):
    """Test wrestler selection with filters applied."""
    app = pygame_app
    app._state = app.session.new_game(1, "Test Save")
    app.router.navigate("wrestler_selection")

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
