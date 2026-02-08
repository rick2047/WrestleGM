"""Visual snapshot tests for SaveSlotSelectionScreen."""

import io

import pygame
import pygame_gui
import pytest
from pygame import Rect

from wrestlegm.ui_pygame.screens.game_hub import GameHubScreen
from wrestlegm.ui_pygame.screens.save_slots import SaveSlotSelectionScreen
from wrestlegm import persistence


def test_save_slots_render(pygame_app, snapshot_image):
    """Test save slot selection screen renders correctly."""
    app = pygame_app
    app.router.navigate("save_slots")

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


def test_save_slots_empty_state(pygame_app, snapshot_image):
    """Test save slots with all empty slots."""
    app = pygame_app
    app.router.navigate("save_slots")

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


def test_save_slots_occupied_state(pygame_app, snapshot_image):
    """Test save slots with some occupied slots."""
    app = pygame_app
    app.router.navigate("save_slots")

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


def test_save_slots_overwrite_guard_rail_modal(pygame_app):
    """Occupied-slot new game enforces overwrite guard rails behaviorally."""
    app = pygame_app

    # Seed occupied slot 1 with a named save.
    seeded_state = app.session.new_game(1, "Test Save")
    app.session.save_current_slot(seeded_state)

    app.router.navigate("save_slots", mode="new")

    current = app.router.current
    assert current is not None
    current.build(app.ui_manager, Rect(0, 0, 480, 800))
    app.ui_manager.update(0.016)

    # Step 1: click occupied slot -> guard-rail warning opens immediately.
    slot_button = current._slot_buttons[0]
    current.handle_event(
        pygame.event.Event(pygame_gui.UI_BUTTON_PRESSED, {"ui_element": slot_button})
    )

    assert app.router.has_active_modal
    modal = app.router._active_modal
    assert modal.window_display_title.startswith("Overwrite Named Save?")
    assert "permanently overwrite" in modal.confirmation_text.html_text
    assert "Test Save" in modal.confirmation_text.html_text
    assert "cannot be undone" in modal.confirmation_text.html_text
    assert modal.confirm_button.text == "OVERWRITE"

    # Cancel path: should keep existing save name unchanged.
    app.router.handle_modal_event(
        pygame.event.Event(
            pygame_gui.UI_BUTTON_PRESSED,
            {"ui_element": modal.cancel_button},
        )
    )
    assert isinstance(app.router.current, SaveSlotSelectionScreen)
    slots_after_cancel = app.session.list_slots()
    slot1_after_cancel = next(
        slot for slot in slots_after_cancel if slot.slot_index == 1
    )
    assert slot1_after_cancel.name == "Test Save"

    # Confirm path: repeat user path, accept warning, then enter replacement name.
    current.handle_event(
        pygame.event.Event(pygame_gui.UI_BUTTON_PRESSED, {"ui_element": slot_button})
    )
    assert app.router.has_active_modal
    modal = app.router._active_modal
    app.router.handle_modal_event(
        pygame.event.Event(
            pygame_gui.UI_BUTTON_PRESSED,
            {"ui_element": modal.confirm_button},
        )
    )

    assert current._name_window is not None
    assert current._name_input is not None
    current._name_input.set_text("Replacement Save")
    current.handle_event(
        pygame.event.Event(
            pygame_gui.UI_BUTTON_PRESSED,
            {"ui_element": current._name_confirm_button},
        )
    )

    # New game start should navigate and stage new slot name for next save.
    assert isinstance(app.router.current, GameHubScreen)
    assert app.session.current_slot_index == 1
    assert app.session.pending_slot_name == "Replacement Save"


def test_occupied_slot_without_name_skips_overwrite_warning(pygame_app):
    """Guard rail only appears for occupied named saves."""
    app = pygame_app

    # Persist a slot with file present but blank name metadata.
    seeded_state = app.session.new_game(1, "Temp")
    app.session.save_current_slot(seeded_state)
    slots = app.session.list_slots()
    slots[0] = persistence.SaveSlotInfo(
        slot_index=1,
        name="",
        exists=True,
        last_saved_show_index=0,
    )
    persistence.save_slot_index(slots, app.session._save_dir)

    app.router.navigate("save_slots", mode="new")
    current = app.router.current
    assert current is not None
    current.build(app.ui_manager, Rect(0, 0, 480, 800))

    current.handle_event(
        pygame.event.Event(
            pygame_gui.UI_BUTTON_PRESSED, {"ui_element": current._slot_buttons[0]}
        )
    )

    assert not app.router.has_active_modal
    assert current._name_window is not None
