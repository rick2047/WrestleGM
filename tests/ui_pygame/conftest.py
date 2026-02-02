"""Pytest fixtures for pygame UI testing."""

import os

import pygame
import pytest
from syrupy.extensions.single_file import SingleFileSnapshotExtension


@pytest.fixture
def snapshot_image(snapshot):
    """Snapshot fixture for pygame surface images."""
    return snapshot.use_extension(SingleFileSnapshotExtension)


@pytest.fixture
def pygame_app():
    """Headless pygame app with fixed clock for deterministic testing."""
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()

    from wrestlegm.ui_pygame import WrestleGMApp

    app = WrestleGMApp()
    # Fix clock for determinism
    app._clock.tick = lambda fps: 16  # Fixed ~60fps
    app._scale = 1.0

    yield app
    pygame.quit()
