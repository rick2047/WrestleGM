"""Visual snapshot tests for ResultsScreen."""

import io

import pytest
import pygame
from pygame import Rect

from wrestlegm.models import (
    MATCH_CATEGORIES,
    Match,
    MatchResult,
    Promo,
    PromoResult,
    Show,
    StatDelta,
)


def _build_show_with_results(app, include_match: bool, include_promo: bool) -> Show:
    wrestlers = list(app.state.roster.values())
    match_types = list(app.state.match_types.values())

    slots = []
    results = []

    if include_match and len(wrestlers) >= 2 and match_types:
        category = MATCH_CATEGORIES[0]
        match = Match(
            wrestlers=[wrestlers[0], wrestlers[1]],
            match_category=category,
            match_type_id=match_types[0].id,
        )
        slots.append(match)
        results.append(
            MatchResult(
                winner_id=wrestlers[0].id,
                non_winner_ids=[wrestlers[1].id],
                rating=3.5,
                match_category=category,
                match_type_id=match_types[0].id,
                applied_modifiers=match_types[0].modifiers,
                stat_deltas={
                    wrestlers[0].id: StatDelta(popularity=1, stamina=-5),
                    wrestlers[1].id: StatDelta(popularity=-1, stamina=-6),
                },
            )
        )

    if include_promo and wrestlers:
        promo = Promo(wrestler=wrestlers[0])
        slots.append(promo)
        results.append(
            PromoResult(
                wrestler_id=wrestlers[0].id,
                rating=2.75,
                stat_deltas={wrestlers[0].id: StatDelta(popularity=1, stamina=-2)},
            )
        )

    return Show(
        show_index=app.state.show_index,
        scheduled_slots=slots,
        results=results,
        show_rating=3.2,
        audience=1200,
        gate_income=5000,
        merch_income=1200,
        total_earned=6200,
        show_cost=3000,
    )


def test_results_render(pygame_app, snapshot_image):
    """Test results screen renders correctly."""
    app = pygame_app
    app._state = app.session.new_game(1, "Test Save")
    show = _build_show_with_results(app, include_match=False, include_promo=False)
    app.router.navigate("results", show=show)

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


def test_results_with_matches(pygame_app, snapshot_image):
    """Test results with match results displayed."""
    app = pygame_app
    app._state = app.session.new_game(1, "Test Save")
    show = _build_show_with_results(app, include_match=True, include_promo=False)
    app.router.navigate("results", show=show)

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


def test_results_with_promos(pygame_app, snapshot_image):
    """Test results with promo results displayed."""
    app = pygame_app
    app._state = app.session.new_game(1, "Test Save")
    show = _build_show_with_results(app, include_match=False, include_promo=True)
    app.router.navigate("results", show=show)

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
