"""Visual snapshot tests for MainMenuScreen."""

import pytest


@pytest.mark.skip(reason="Snapshot testing requires running pygame - update manually")
def test_main_menu_render(pygame_app, snapshot_image):
    """Test main menu renders correctly."""
    app = pygame_app
    app.router.navigate("main_menu")
    # Build screen
    from pygame import Rect

    current = app.router.current
    if current:
        current.build(app.ui_manager, Rect(0, 0, 480, 800))

    # Process a frame to render
    app.ui_manager.update(0.016)  # ~60fps

    # Capture would go here with full implementation
    # For now, this is a placeholder structure
    assert True


@pytest.mark.skip(reason="Snapshot testing requires running pygame - update manually")
def test_main_menu_buttons_visible(pygame_app, snapshot_image):
    """Test all main menu buttons are visible and accessible."""
    # Verify New Game, Load Game, Quit buttons
    pass
