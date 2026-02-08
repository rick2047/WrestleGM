"""Save slot selection screen for WrestleGM pygame UI."""

from __future__ import annotations

import pygame
import pygame_gui
from pygame.rect import Rect
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIButton, UILabel, UIPanel, UITextEntryLine, UIWindow

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
        self._name_window: UIWindow | None = None
        self._name_input: UITextEntryLine | None = None
        self._name_confirm_button: UIButton | None = None
        self._name_cancel_button: UIButton | None = None
        self._pending_slot_index: int | None = None

    def _build_header(self, manager, rect) -> None:
        """Build header with title and back button."""
        from ..constants import MARGIN

        # Title based on mode
        title_text = "LOAD GAME" if self._mode == "load" else "NEW GAME"

        # Back button on the left
        back_rect = Rect(rect.x + MARGIN, rect.y + 10, 80, 30)
        self._back_button = UIButton(
            relative_rect=back_rect,
            text="← BACK",
            manager=manager,
            object_id=ObjectID(
                class_id="@secondary_button", object_id="#save_slots_back_button"
            ),
        )

        # Title label centered
        title_rect = Rect(rect.x, rect.y + 10, rect.width, 30)
        self._title_label = UILabel(
            relative_rect=title_rect,
            text=title_text,
            manager=manager,
            object_id=ObjectID(class_id="@header_title", object_id="#save_slots_title"),
        )

    def _build_body(self, manager, rect) -> None:
        """Build body with save slot grid."""
        self._slot_buttons.clear()
        self._slot_panels.clear()

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
                object_id=ObjectID(
                    class_id="@save_slot_panel", object_id=f"#save_slot_panel_{i + 1}"
                ),
            )
            self._slot_panels.append(panel)

            # Add slot content
            self._build_slot_content(manager, panel, slot, slot_rect)

    def _build_slot_content(self, manager, panel, slot, slot_rect) -> None:
        """Build content for a single save slot."""
        padding = 8
        content_x = padding
        content_y = padding
        content_width = slot_rect.width - (padding * 2)

        # Slot number header
        slot_header_rect = Rect(content_x, content_y, content_width, 24)
        UILabel(
            relative_rect=slot_header_rect,
            text=f"Slot {slot.slot_index}",
            manager=manager,
            container=panel,
            object_id=ObjectID(class_id="@save_slot_header"),
        )

        # Create clickable button first so informational labels render above it.
        button_rect = Rect(0, 0, slot_rect.width, slot_rect.height)
        button_tooltip = (
            f"Load {slot.name or 'save'}" if slot.exists else "Start new game here"
        )
        button = UIButton(
            relative_rect=button_rect,
            text="",
            manager=manager,
            container=panel,
            tool_tip_text=button_tooltip,
            object_id=ObjectID(
                class_id="@save_slot_button",
                object_id=f"#save_slot_button_{slot.slot_index}",
            ),
        )
        if self._mode == "load" and not slot.exists:
            button.disable()
        self._slot_buttons.append(button)

        if slot.exists:
            # Occupied slot - show details
            show_index = (slot.last_saved_show_index or 0) + 1
            name = slot.name or "Unnamed"

            name_rect = Rect(content_x, content_y + 24, content_width, 20)
            UILabel(
                relative_rect=name_rect,
                text=name,
                manager=manager,
                container=panel,
                object_id=ObjectID(class_id="@save_slot_name"),
            )

            show_rect = Rect(content_x, content_y + 44, content_width, 20)
            UILabel(
                relative_rect=show_rect,
                text=f"Show #{show_index}",
                manager=manager,
                container=panel,
                object_id=ObjectID(class_id="@save_slot_meta"),
            )
        else:
            # Empty slot
            empty_rect = Rect(content_x, content_y + 24, content_width, 40)
            UILabel(
                relative_rect=empty_rect,
                text="[ EMPTY ]",
                manager=manager,
                container=panel,
                object_id=ObjectID(class_id="@save_slot_empty"),
            )

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
            object_id=ObjectID(class_id="@footer_hint", object_id="#save_slots_hint"),
        )

    def _load_slots(self) -> list[persistence.SaveSlotInfo]:
        """Load save slot information from SessionManager."""
        # Access SessionManager through app
        if hasattr(self._app, "session"):
            raw_slots = self._app.session.list_slots()
            save_dir = self._app.session._save_dir
            normalized: list[persistence.SaveSlotInfo] = []

            for slot in raw_slots:
                has_file = persistence.slot_path(slot.slot_index, save_dir).exists()
                name = slot.name.strip() if isinstance(slot.name, str) else None
                if name == "":
                    name = None
                exists = bool(slot.exists and has_file)

                normalized.append(
                    persistence.SaveSlotInfo(
                        slot_index=slot.slot_index,
                        name=name if exists else None,
                        exists=exists,
                        last_saved_show_index=(
                            slot.last_saved_show_index if exists else None
                        ),
                    )
                )

            return normalized
        # Fallback: return default empty slots
        return persistence.default_slots()

    def handle_event(self, event) -> bool:
        """Handle button press events."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if self._name_window is not None:
                if event.ui_element == self._name_confirm_button:
                    self._confirm_new_game_name()
                    return True
                if event.ui_element == self._name_cancel_button:
                    self._close_name_modal()
                    return True

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
        if self._name_window is not None:
            return

        # Find the slot info
        slot = None
        for s in self._slots:
            if s.slot_index == slot_number:
                slot = s
                break

        if slot is None:
            return

        if self._mode == "new":
            if slot.exists and slot.name:
                # Guard rail first for occupied slot
                self._show_overwrite_modal(
                    slot_index=slot.slot_index,
                    existing_name=slot.name,
                )
            else:
                self._show_name_modal(slot_number)
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

    def _start_new_game(self, slot_index: int) -> None:
        self._start_new_game_with_name(slot_index, f"Slot {slot_index}")

    def _start_new_game_with_name(self, slot_index: int, slot_name: str) -> None:
        """Start a new game in the specified slot."""
        # Use SessionManager to create new game
        if hasattr(self._app, "session"):
            # Access internal _state directly since state is a read-only property
            self._app._state = self._app.session.new_game(slot_index, slot_name)
            # Navigate to game hub
            self._router.navigate("game_hub")

    def _show_name_modal(self, slot_index: int) -> None:
        """Show modal to capture new save name."""
        if self._name_window is not None:
            return

        self._pending_slot_index = slot_index
        self._name_window = UIWindow(
            rect=Rect(80, 260, 320, 180),
            manager=self._app.ui_manager,
            window_display_title=f"New Game - Slot {slot_index}",
            object_id=ObjectID(class_id="@modal_window", object_id="#save_name_window"),
        )

        self._name_input = UITextEntryLine(
            relative_rect=Rect(20, 40, 280, 32),
            manager=self._app.ui_manager,
            container=self._name_window,
            initial_text="",
            placeholder_text="Enter save name",
            object_id=ObjectID(class_id="@text_input", object_id="#save_name_input"),
        )

        self._name_confirm_button = UIButton(
            relative_rect=Rect(60, 100, 90, 32),
            text="START",
            manager=self._app.ui_manager,
            container=self._name_window,
            object_id=ObjectID(
                class_id="@primary_button", object_id="#save_name_confirm"
            ),
        )
        self._name_cancel_button = UIButton(
            relative_rect=Rect(170, 100, 90, 32),
            text="CANCEL",
            manager=self._app.ui_manager,
            container=self._name_window,
            object_id=ObjectID(
                class_id="@secondary_button", object_id="#save_name_cancel"
            ),
        )
        self._name_input.focus()

    def _confirm_new_game_name(self) -> None:
        if self._pending_slot_index is None or self._name_input is None:
            return

        slot_name = self._name_input.get_text().strip()
        if not slot_name:
            self._show_error_modal("Save Name Required", "Please enter a save name.")
            return

        slot_index = self._pending_slot_index
        self._close_name_modal()
        self._start_new_game_with_name(slot_index, slot_name)

    def _close_name_modal(self) -> None:
        if self._name_window is not None:
            self._name_window.kill()
        self._name_window = None
        self._name_input = None
        self._name_confirm_button = None
        self._name_cancel_button = None
        self._pending_slot_index = None

    def _show_overwrite_modal(self, slot_index: int, existing_name: str) -> None:
        """Show overwrite confirmation for occupied slots in new-game flow."""

        def on_confirm() -> None:
            self._show_name_modal(slot_index)

        warning_message = (
            f'WARNING: This will permanently overwrite "{existing_name}" in Slot {slot_index}.\n\n'
            "This action cannot be undone.\n\n"
            "If you continue, you will be prompted to enter the new save name."
        )

        self._router.show_confirm(
            title=f"Overwrite Named Save? (Slot {slot_index})",
            message=warning_message,
            on_confirm=on_confirm,
            on_cancel=None,
            confirm_text="OVERWRITE",
            cancel_text="No",
        )

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
