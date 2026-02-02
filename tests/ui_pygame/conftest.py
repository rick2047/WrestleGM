"""Pytest fixtures for pygame UI testing."""

import os

import pygame
import pytest
from syrupy.extensions.image import PNGImageSnapshotExtension


@pytest.fixture
def snapshot_image(snapshot):
    """Snapshot fixture for pygame surface images."""
    return snapshot.use_extension(PNGImageSnapshotExtension)


@pytest.fixture
def pygame_app():
    """Headless pygame app with fixed clock for deterministic testing."""
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()

    from wrestlegm.ui_pygame import WrestleGMApp

    app = WrestleGMApp()
    # Fix clock for determinism
    app._clock.tick = lambda fps: 16  # Fixed ~60fps

    yield app
    pygame.quit()


@pytest.fixture
def app_with_built_screen():
    """App with main_menu screen built and ready for interaction testing."""
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    from wrestlegm.ui_pygame import WrestleGMApp
    from pygame import Rect

    app = WrestleGMApp()
    app.router.navigate("main_menu")
    screen = app.router.current
    screen.build(app.ui_manager, Rect(0, 0, 480, 800))

    yield app
    pygame.quit()


@pytest.fixture
def navigation_tracker(app_with_built_screen):
    """Monkey-patches router.navigate to record all navigation calls."""
    app = app_with_built_screen
    tracker = []
    original_navigate = app.router.navigate

    def tracked_navigate(route, **kwargs):
        tracker.append((route, kwargs))
        return original_navigate(route, **kwargs)

    app.router.navigate = tracked_navigate
    yield tracker


@pytest.fixture
def create_button_click_event():
    """Helper function to create UI_BUTTON_PRESSED events for testing."""

    def _create(button_element):
        import pygame
        import pygame_gui

        return pygame.event.Event(
            pygame_gui.UI_BUTTON_PRESSED, {"ui_element": button_element}
        )

    return _create
