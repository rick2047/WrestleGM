"""Visual snapshot tests for GameHubScreen."""

import io

import pytest
import pygame
from pygame import Rect


def test_game_hub_render(pygame_app, snapshot_image):
    """Test game hub renders correctly."""
    app = pygame_app
    # Setup game state
    app.state.new_game()
    app.router.navigate("game_hub")

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


def test_game_hub_with_data(pygame_app, snapshot_image):
    """Test game hub with active game data."""
    app = pygame_app
    app.state.new_game()
    app.router.navigate("game_hub")

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
