"""Save slot selection screen for WrestleGM pygame UI."""

from __future__ import annotations

import pygame
import pygame_gui
from pygame.rect import Rect
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIButton, UILabel, UIPanel

from wrestlegm import persistence

from .base import BaseScreen


class SaveSlotSelectionScreen(BaseScreen):
    """Save slot selection for new/load game."""

    # Grid layout constants
    SLOT_COUNT = 6
    GRID_COLS = 2
    GRID_ROWS = 3

    def __init__(self, app, router, mode="new") -> None:
        super().__init__(app, router)
        self._mode = mode  # "new" or "load"
        self._slots: list[persistence.SaveSlotInfo] = []
        self._slot_buttons: list[pygame_gui.elements.UIButton] = []
        self._slot_panels: list[pygame_gui.elements.UIPanel] = []
        self._back_button: pygame_gui.elements.UIButton | None = None
        self._title_label: pygame_gui.elements.UILabel | None = None

    def _build_header(self, manager, rect) -> None:
        """Build header with title and back button."""
        from ..constants import MARGIN, PADDING

        # Title based on mode
        title_text = "LOAD GAME" if self._mode == "load" else "NEW GAME"

        # Back button on the left
        back_rect = Rect(rect.x + MARGIN, rect.y + 10, 80, 30)
        self._back_button = UIButton(
            relative_rect=back_rect,
            text="← BACK",
            manager=manager,
            object_id=ObjectID(class_id="@secondary_button"),
        )

        # Title label centered
        title_rect = Rect(rect.x, rect.y + 10, rect.width, 30)
        self._title_label = UILabel(
            relative_rect=title_rect,
            text=title_text,
            manager=manager,
            object_id=ObjectID(class_id="@header_title"),
        )

    def _build_body(self, manager, rect) -> None:
        """Build body with save slot grid."""
        from ..constants import MARGIN, PADDING

        # Load slot data
        self._slots = self._load_slots()

        # Calculate grid layout
        grid_padding = 16
        slot_margin = 12

        # Available space for the grid
        available_width = rect.width - (grid_padding * 2)
        available_height = rect.height - (grid_padding * 2)

        # Calculate slot dimensions
        slot_width = (available_width - slot_margin) // self.GRID_COLS
        slot_height = (available_height - slot_margin * 2) // self.GRID_ROWS

        # Start position
        start_x = rect.x + grid_padding
        start_y = rect.y + grid_padding

        # Create slot panels and buttons
        for i, slot in enumerate(self._slots):
            row = i // self.GRID_COLS
            col = i % self.GRID_COLS

            # Calculate position
            slot_x = start_x + col * (slot_width + slot_margin)
            slot_y = start_y + row * (slot_height + slot_margin)

            # Create slot panel
            slot_rect = Rect(slot_x, slot_y, slot_width, slot_height)
            panel = UIPanel(
                relative_rect=slot_rect,
                manager=manager,
            )
            self._slot_panels.append(panel)

            # Add slot content
            self._build_slot_content(manager, panel, slot, slot_rect)

    def _build_slot_content(self, manager, panel, slot, slot_rect) -> None:
        """Build content for a single save slot."""
        from ..constants import FONT_SIZE_BODY, FONT_SIZE_STATS

        padding = 8
        content_x = slot_rect.x + padding
        content_y = slot_rect.y + padding
        content_width = slot_rect.width - (padding * 2)

        # Slot number header
        slot_header_rect = Rect(content_x, content_y, content_width, 24)
        UILabel(
            relative_rect=slot_header_rect,
            text=f"Slot {slot.slot_index}",
            manager=manager,
            container=panel,
        )

        if slot.exists:
            # Occupied slot - show details
            show_index = (slot.last_saved_show_index or 0) + 1
            name = slot.name or "Unnamed"

            # Name
            name_rect = Rect(content_x, content_y + 24, content_width, 20)
            UILabel(
                relative_rect=name_rect,
                text=name,
                manager=manager,
                container=panel,
            )

            # Show number
            show_rect = Rect(content_x, content_y + 44, content_width, 20)
            UILabel(
                relative_rect=show_rect,
                text=f"Show #{show_index}",
                manager=manager,
                container=panel,
            )

            # Create clickable button overlay
            button_rect = Rect(
                slot_rect.x, slot_rect.y, slot_rect.width, slot_rect.height
            )
            button = UIButton(
                relative_rect=button_rect,
                text="",
                manager=manager,
                tool_tip_text=f"Load {name}",
            )
            self._slot_buttons.append(button)
        else:
            # Empty slot
            empty_rect = Rect(content_x, content_y + 24, content_width, 40)
            UILabel(
                relative_rect=empty_rect,
                text="[ EMPTY ]",
                manager=manager,
                container=panel,
            )

            # Create clickable button overlay (only enabled for new game mode)
            button_rect = Rect(
                slot_rect.x, slot_rect.y, slot_rect.width, slot_rect.height
            )
            button = UIButton(
                relative_rect=button_rect,
                text="",
                manager=manager,
                tool_tip_text="Start new game here",
            )
            # Disable button for empty slots in load mode
            if self._mode == "load":
                button.disable()
            self._slot_buttons.append(button)

    def _build_actions(self, manager, rect) -> None:
        """No action buttons needed for save slot screen."""
        pass

    def _build_footer(self, manager, rect) -> None:
        """Build footer with hint text."""
        hint_text = (
            "Select a save slot to load"
            if self._mode == "load"
            else "Select an empty slot to start a new game"
        )
        hint_rect = Rect(rect.x, rect.y + 10, rect.width, 20)
        UILabel(
            relative_rect=hint_rect,
            text=hint_text,
            manager=manager,
        )

    def _load_slots(self) -> list[persistence.SaveSlotInfo]:
        """Load save slot information from SessionManager."""
        # Access SessionManager through app
        if hasattr(self._app, "session"):
            return self._app.session.list_slots()
        # Fallback: return default empty slots
        return persistence.default_slots()

    def handle_event(self, event) -> bool:
        """Handle button press events."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self._back_button:
                self._on_back()
                return True

            # Check if a slot button was clicked
            for i, button in enumerate(self._slot_buttons):
                if event.ui_element == button:
                    self._on_slot_clicked(i + 1)  # Slot numbers are 1-based
                    return True

        return False

    def _on_back(self) -> None:
        """Go back to main menu."""
        self._router.back()

    def _on_slot_clicked(self, slot_number: int) -> None:
        """Handle slot selection."""
        # Find the slot info
        slot = None
        for s in self._slots:
            if s.slot_index == slot_number:
                slot = s
                break

        if slot is None:
            return

        if self._mode == "new":
            if slot.exists:
                # Show overwrite confirmation modal
                self._show_overwrite_modal(slot)
            else:
                # Start new game in empty slot
                self._start_new_game(slot_number)
        else:  # load mode
            if slot.exists:
                try:
                    # Load the game
                    self._load_game(slot_number)
                except Exception as e:
                    # Show error modal for corrupt save
                    self._show_error_modal("Corrupt Save", "Save file is corrupted.")
            else:
                # Show "no save data" error
                self._show_error_modal("No Save Data", "This slot is empty.")

    def _show_error_modal(self, title: str, message: str) -> None:
        """Show an error modal via Router."""
        self._router.show_error(title, message)

    def _show_overwrite_modal(self, slot: persistence.SaveSlotInfo) -> None:
        """Show overwrite confirmation modal via Router."""
        slot_index = slot.slot_index  # Capture slot_index for closure

        def on_confirm():
            self._start_new_game(slot_index)

        def on_cancel():
            pass

        self._router.show_confirm(
            title=f"Overwrite Slot {slot.slot_index}?",
            message=f'This will replace "{slot.name or "Unnamed"}".',
            on_confirm=on_confirm,
            on_cancel=on_cancel,
            confirm_text="Yes",
            cancel_text="No",
        )

    def _start_new_game(self, slot_index: int) -> None:
        """Start a new game in the specified slot."""
        # Use SessionManager to create new game
        if hasattr(self._app, "session"):
            # Access internal _state directly since state is a read-only property
            self._app._state = self._app.session.new_game(
                slot_index, f"Slot {slot_index}"
            )
            # Navigate to game hub
            self._router.navigate("game_hub")

    def _load_game(self, slot_index: int) -> None:
        """Load a game from the specified slot."""
        if hasattr(self._app, "session"):
            try:
                # Access internal _state directly since state is a read-only property
                self._app._state = self._app.session.load_game(slot_index)
                # Navigate to game hub
                self._router.navigate("game_hub")
            except ValueError as exc:
                # Handle various load errors
                message = "Unable to load save."
                if str(exc) == "unsupported_save_version":
                    message = "Save version unsupported."
                elif str(exc) == "corrupt_save_file":
                    message = "Save file is corrupt."
                elif str(exc) in {"empty_slot", "missing_save_file"}:
                    message = "Save file is missing."
                self._show_error_modal("Load Error", message)
                raise
