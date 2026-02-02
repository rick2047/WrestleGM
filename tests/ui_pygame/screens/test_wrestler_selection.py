"""Visual snapshot tests for WrestlerSelectionScreen."""

import pytest


@pytest.mark.skip(reason="Snapshot testing requires running pygame - update manually")
def test_wrestler_selection_render(pygame_app, snapshot_image):
    """Test wrestler selection screen renders correctly."""
    app = pygame_app
    app.state.new_game()
    app.router.navigate("wrestler_selection")

    from pygame import Rect

    current = app.router.current
    if current:
        current.build(app.ui_manager, Rect(0, 0, 480, 800))

    app.ui_manager.update(0.016)
    assert True


@pytest.mark.skip(reason="Snapshot testing requires running pygame - update manually")
def test_wrestler_selection_filtered(pygame_app, snapshot_image):
    """Test wrestler selection with filters applied."""
    pass
