"""Visual snapshot tests for MainMenuScreen."""

import io

import pytest
import pygame
from pygame import Rect


def test_main_menu_render(pygame_app, snapshot_image):
    """Test main menu renders correctly."""
    app = pygame_app
    app.router.navigate("main_menu")

    # Build screen
    current = app.router.current
    if current:
        current.build(app.ui_manager, Rect(0, 0, 480, 800))

    # Process a frame to render
    app.ui_manager.update(0.016)

    # Render to surface and capture
    surface = pygame.Surface((480, 800))
    app.ui_manager.draw_ui(surface)

    # Capture and compare
    buffer = io.BytesIO()
    pygame.image.save(surface, buffer, ".png")
    assert buffer.getvalue() == snapshot_image


def test_main_menu_buttons_visible(pygame_app, snapshot_image):
    """Test all main menu buttons are visible and accessible."""
    app = pygame_app
    app.router.navigate("main_menu")

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
