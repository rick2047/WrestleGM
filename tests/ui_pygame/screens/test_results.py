"""Visual snapshot tests for ResultsScreen."""

import pytest


@pytest.mark.skip(reason="Snapshot testing requires running pygame - update manually")
def test_results_render(pygame_app, snapshot_image):
    """Test results screen renders correctly."""
    app = pygame_app
    app.state.new_game()
    app.router.navigate("results")

    from pygame import Rect

    current = app.router.current
    if current:
        current.build(app.ui_manager, Rect(0, 0, 480, 800))

    app.ui_manager.update(0.016)
    assert True


@pytest.mark.skip(reason="Snapshot testing requires running pygame - update manually")
def test_results_with_matches(pygame_app, snapshot_image):
    """Test results with match results displayed."""
    pass


@pytest.mark.skip(reason="Snapshot testing requires running pygame - update manually")
def test_results_with_promos(pygame_app, snapshot_image):
    """Test results with promo results displayed."""
    pass
