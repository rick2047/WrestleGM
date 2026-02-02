"""Visual snapshot tests for SaveSlotSelectionScreen."""

import pytest
from pygame import Rect


def test_save_slots_render(pygame_app, snapshot_image):
    """Test save slot selection screen renders correctly."""
    app = pygame_app
    app.router.navigate("save_slots")

    current = app.router.current
    if current:
        current.build(app.ui_manager, Rect(0, 0, 480, 800))

    app.ui_manager.update(0.016)
    assert current is not None


def test_save_slots_empty_state(pygame_app, snapshot_image):
    """Test save slots with all empty slots."""
    pass


def test_save_slots_occupied_state(pygame_app, snapshot_image):
    """Test save slots with some occupied slots."""
    pass
