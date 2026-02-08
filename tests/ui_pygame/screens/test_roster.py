"""Visual and behavior tests for RosterScreen."""

import io

import pygame
from pygame import Rect
from pygame_gui.elements import UIImage


def test_roster_render(pygame_app, snapshot_image):
    """Roster screen renders wrestler cards correctly."""
    app = pygame_app
    app._state = app.session.new_game(1, "Test Save")
    app.router.navigate("roster")

    current = app.router.current
    assert current is not None
    current.build(app.ui_manager, Rect(0, 0, 480, 800))

    app.ui_manager.update(0.016)

    surface = pygame.Surface((480, 800))
    app.ui_manager.draw_ui(surface)

    buffer = io.BytesIO()
    pygame.image.save(surface, buffer, ".png")
    assert buffer.getvalue() == snapshot_image


def test_roster_uses_wrestler_cards_with_inspect_action(pygame_app):
    """Roster uses shared wrestler card layout with inspect actions."""
    app = pygame_app
    app._state = app.session.new_game(1, "Test Save")
    app.router.navigate("roster")

    current = app.router.current
    assert current is not None
    current.build(app.ui_manager, Rect(0, 0, 480, 800))

    assert current._wrestler_cards
    first_card = current._wrestler_cards[0]
    assert first_card.action_button.text == "INSPECT"
    assert (
        "[F]" in first_card.alignment_label.text
        or "[H]" in first_card.alignment_label.text
    )
    assert isinstance(first_card.avatar_image, UIImage)
