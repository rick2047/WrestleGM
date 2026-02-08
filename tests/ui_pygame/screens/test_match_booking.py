"""Visual snapshot tests for MatchBookingScreen."""

import io

import pytest
import pygame
from pygame import Rect

from wrestlegm.models import MATCH_CATEGORIES, Match
from wrestlegm.ui_pygame.screens.match_booking import MatchBookingScreen
from wrestlegm.ui_pygame.screens.wrestler_selection import WrestlerSelectionScreen


def test_match_booking_render(pygame_app, snapshot_image):
    """Test match booking screen renders correctly."""
    app = pygame_app
    app._state = app.session.new_game(1, "Test Save")
    app.router.navigate("match_booking")

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


def test_match_booking_with_selections(pygame_app, snapshot_image):
    """Test match booking with wrestlers selected."""
    app = pygame_app
    app._state = app.session.new_game(1, "Test Save")
    wrestlers = list(app._state.roster.values())[:2]
    existing_match = Match(
        wrestlers=wrestlers,
        match_category=MATCH_CATEGORIES[0],
        match_type_id=list(app._state.match_types.keys())[0],
    )
    app.router.navigate("match_booking", slot_index=0, existing_match=existing_match)

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


def test_match_booking_wrestler_selection_round_trip(app_with_interaction):
    """Clicking '+' in wrestler selection applies selection and returns."""
    app = app_with_interaction

    app.router.navigate("match_booking", slot_index=0)
    app.pump_events()
    assert isinstance(app.router.current, MatchBookingScreen)

    # Open wrestler selection from first slot
    app.click(app.router.current._wrestler_slot_buttons[0])
    app.pump_events()
    assert isinstance(app.router.current, WrestlerSelectionScreen)
    assert app.router.current._wrestler_buttons

    # Select first available wrestler (+)
    app.click(app.router.current._wrestler_buttons[0])
    app.pump_events()

    # Back on match booking with selected wrestler persisted
    assert isinstance(app.router.current, MatchBookingScreen)
    assert app.router.current._draft_wrestler_ids[0] is not None
    assert app.router.current._wrestler_slot_buttons[0].text != "SELECT WRESTLER"
