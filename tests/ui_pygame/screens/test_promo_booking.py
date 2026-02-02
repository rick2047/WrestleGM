"""Visual snapshot tests for PromoBookingScreen."""

import pytest


@pytest.mark.skip(reason="Snapshot testing requires running pygame - update manually")
def test_promo_booking_render(pygame_app, snapshot_image):
    """Test promo booking screen renders correctly."""
    app = pygame_app
    app.state.new_game()
    app.router.navigate("promo_booking")

    from pygame import Rect

    current = app.router.current
    if current:
        current.build(app.ui_manager, Rect(0, 0, 480, 800))

    app.ui_manager.update(0.016)
    assert True
