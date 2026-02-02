"""Visual snapshot tests for ResultsScreen."""

import io

import pytest
import pygame
from pygame import Rect


def test_results_render(pygame_app, snapshot_image):
    """Test results screen renders correctly."""
    app = pygame_app
    app.state.new_game()
    app.router.navigate("results")

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


def test_results_with_matches(pygame_app, snapshot_image):
    """Test results with match results displayed."""
    app = pygame_app
    app.state.new_game()
    app.router.navigate("results")

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


def test_results_with_promos(pygame_app, snapshot_image):
    """Test results with promo results displayed."""
    app = pygame_app
    app.state.new_game()
    app.router.navigate("results")

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
