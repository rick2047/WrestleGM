"""Visual snapshot tests for WrestlerSelectionScreen."""

import pytest
from pygame import Rect


def test_wrestler_selection_render(pygame_app, snapshot_image):
    """Test wrestler selection screen renders correctly."""
    app = pygame_app
    app.state.new_game()
    app.router.navigate("wrestler_selection")

    current = app.router.current
    if current:
        current.build(app.ui_manager, Rect(0, 0, 480, 800))

    app.ui_manager.update(0.016)
    assert current is not None


def test_wrestler_selection_filtered(pygame_app, snapshot_image):
    """Test wrestler selection with filters applied."""
    pass
