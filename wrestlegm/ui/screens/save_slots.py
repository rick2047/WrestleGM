"""Save slot selection and naming screens."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static

from wrestlegm import persistence

from ..routes import MAIN_MENU
from .standard import StandardScreen


class SaveSlotSelectionScreen(StandardScreen):
    """Shared screen for selecting save slots."""

    BINDINGS = [
        ("enter", "select", "Select"),
        ("up", "focus_prev", "Prev"),
        ("down", "focus_next", "Next"),
        ("escape", "back", "Back"),
    ]

    def __init__(self, *, mode: str) -> None:
        super().__init__()
        self.mode = mode
        self.slots: list[persistence.SaveSlotInfo] = []
        self.slot_buttons: list[Button] = []

    def header_title(self) -> str:
        return "Load Game" if self.mode == "load" else "New Game"

    def compose_body(self) -> ComposeResult:
        """Build the save slot selection layout."""

        self.slots = self.app.session.list_slots()
        with Vertical(classes="booking-slot-group") as slot_group:
            self.slot_group = slot_group
            for slot in self.slots:
                button = Button(
                    "",
                    id=f"slot-{slot.slot_index}",
                    classes="booking-slot-button",
                )
                self.slot_buttons.append(button)
                yield button

    def on_mount(self) -> None:
        """Load slots and focus the selection."""

        super().on_mount()
        self.refresh_view()
        self._focus_default_slot()

    def _focus_default_slot(self) -> None:
        """Focus the first selectable slot button."""

        for slot, button in zip(self.slots, self.slot_buttons):
            if self._is_slot_active(slot) and not button.disabled:
                button.focus()
                return
        if self.mode != "load" and self.slot_buttons:
            self.slot_buttons[0].focus()

    def refresh_view(self) -> None:
        """Reload slot metadata and update the buttons."""

        self.slots = self.app.session.list_slots()
        if len(self.slots) != len(self.slot_buttons):
            self._rebuild_buttons()
        for slot, button in zip(self.slots, self.slot_buttons):
            button.label = self._slot_label(slot)
            button.disabled = not self._is_slot_active(slot)

    def _rebuild_buttons(self) -> None:
        """Rebuild the slot buttons when slot counts change."""

        if hasattr(self, "slot_group"):
            for child in list(self.slot_group.children):
                child.remove()
        self.slot_buttons = []
        if hasattr(self, "slot_group"):
            for slot in self.slots:
                button = Button(
                    "",
                    id=f"slot-{slot.slot_index}",
                    classes="booking-slot-button",
                )
                self.slot_buttons.append(button)
                self.slot_group.mount(button)

    def _slot_label(self, slot: persistence.SaveSlotInfo) -> str:
        """Format a slot label for display."""

        if slot.exists:
            show_index = (slot.last_saved_show_index or 0) + 1
            name = slot.name or "Unnamed"
            return f"Slot {slot.slot_index} · {name} · Show #{show_index}"
        empty_label = f"Slot {slot.slot_index} · [ Empty ]"
        if self.mode == "load":
            return f"[dim]{empty_label}[/dim]"
        return empty_label

    def _is_slot_active(self, slot: persistence.SaveSlotInfo) -> bool:
        """Return whether a slot is selectable in the current mode."""

        if self.mode != "load":
            return True
        return slot.exists

    def _slot_for_button(self, button: Button) -> persistence.SaveSlotInfo | None:
        """Map a slot button back to slot metadata."""

        if button.id is None:
            return None
        try:
            slot_index = int(button.id.replace("slot-", ""))
        except ValueError:
            return None
        for slot in self.slots:
            if slot.slot_index == slot_index:
                return slot
        return None

    def action_select(self) -> None:
        """Handle selection based on mode and slot state."""

        focused = self.app.focused
        if isinstance(focused, Button) and focused in self.slot_buttons:
            self._select_slot(focused)
            return
        self._focus_default_slot()

    def _select_slot(self, button: Button) -> None:
        """Handle selection based on mode and slot state."""

        slot = self._slot_for_button(button)
        if slot is None:
            return
        if self.mode == "load":
            if not slot.exists:
                return
            self.app.call_later(self.app.load_game, slot.slot_index)
            return
        if slot.exists:
            self.app.push_screen(
                OverwriteSaveSlotModal(slot_index=slot.slot_index, slot_name=slot.name or ""),
                lambda result: self._handle_overwrite(slot, result),
            )
            return
        self._prompt_for_name(slot.slot_index, "", overwrite=False)

    def _handle_overwrite(self, slot: persistence.SaveSlotInfo, result: bool | None) -> None:
        """Handle overwrite confirmation result."""

        if result:
            self._prompt_for_name(slot.slot_index, slot.name or "", overwrite=True)

    def _prompt_for_name(self, slot_index: int, initial_name: str, *, overwrite: bool) -> None:
        """Prompt for a slot name before starting a new game."""

        self.app.push_screen(
            NameSaveSlotModal(initial_name=initial_name),
            lambda name: self._start_new_game(slot_index, name, overwrite=overwrite),
        )

    def _start_new_game(self, slot_index: int, name: str | None, *, overwrite: bool) -> None:
        """Start a new game after naming a slot."""

        if name is None:
            return
        if overwrite:
            self.app.session.clear_save_slot(slot_index)
        self.app.new_game(slot_index, name)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle slot button presses."""

        if event.button in self.slot_buttons:
            self._select_slot(event.button)

    def action_focus_next(self) -> None:
        """Move focus down the slot list."""

        self._move_focus(1)

    def action_focus_prev(self) -> None:
        """Move focus up the slot list."""

        self._move_focus(-1)

    def _move_focus(self, delta: int) -> None:
        """Cycle focus between slot buttons."""

        if not self.slot_buttons:
            return
        focused = self.app.focused
        if focused not in self.slot_buttons:
            self._focus_default_slot()
            return
        index = self.slot_buttons.index(focused)
        next_index = index
        for _ in range(len(self.slot_buttons)):
            next_index = (next_index + delta) % len(self.slot_buttons)
            candidate = self.slot_buttons[next_index]
            if not candidate.disabled:
                candidate.focus()
                return

    def action_back(self) -> None:
        """Return to the main menu."""

        self.app.navigate(MAIN_MENU)


class NameSaveSlotModal(ModalScreen):
    """Modal prompt for naming a save slot."""

    BINDINGS = [
        ("enter", "activate", "Confirm"),
        ("escape", "cancel", "Cancel"),
        ("up", "focus_prev", "Prev"),
        ("down", "focus_next", "Next"),
    ]

    def __init__(self, *, initial_name: str) -> None:
        super().__init__()
        self.initial_name = initial_name

    def compose(self) -> ComposeResult:
        """Build the name slot modal layout."""

        with Vertical(classes="panel"):
            yield Static("Name Save Slot")
            self.name_input = Input(value=self.initial_name, placeholder="Slot name")
            yield self.name_input
            self.confirm_button = Button("Confirm", id="confirm")
            self.cancel_button = Button("Cancel", id="cancel")
            yield self.confirm_button
            yield self.cancel_button

    def on_mount(self) -> None:
        """Focus input and set initial button state."""

        self.name_input.focus()
        self._update_confirm_state()

    def _update_confirm_state(self) -> None:
        """Enable or disable confirm based on input value."""

        self.confirm_button.disabled = not self._is_name_valid()

    def _is_name_valid(self) -> bool:
        """Return True when the input has a non-empty name."""

        return bool(self.name_input.value.strip())

    def on_input_changed(self, event: Input.Changed) -> None:
        """Update confirm button as the name changes."""

        if event.input is self.name_input:
            self._update_confirm_state()

    def action_cancel(self) -> None:
        """Cancel naming and close the modal."""

        self.dismiss(result=None)

    def action_activate(self) -> None:
        """Activate the focused button or confirm input."""

        focused = self.app.focused
        if focused is self.name_input:
            if self._is_name_valid():
                self.dismiss(result=self.name_input.value.strip())
            return
        if isinstance(focused, Button) and not focused.disabled:
            focused.press()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle confirm and cancel actions."""

        if event.button.id == "confirm":
            if not self._is_name_valid():
                return
            self.dismiss(result=self.name_input.value.strip())
        elif event.button.id == "cancel":
            self.dismiss(result=None)

    def action_focus_next(self) -> None:
        """Move focus to the next modal action."""

        self._move_focus(1)

    def action_focus_prev(self) -> None:
        """Move focus to the previous modal action."""

        self._move_focus(-1)

    def _move_focus(self, delta: int) -> None:
        """Cycle focus between modal elements."""

        focus_order = [self.name_input, self.confirm_button, self.cancel_button]
        focused = self.app.focused
        if focused not in focus_order:
            focus_order[0].focus()
            return
        index = focus_order.index(focused)
        for _ in range(len(focus_order)):
            index = (index + delta) % len(focus_order)
            candidate = focus_order[index]
            if getattr(candidate, "disabled", False):
                continue
            candidate.focus()
            return


class OverwriteSaveSlotModal(ModalScreen):
    """Modal confirmation for overwriting a save slot."""

    BINDINGS = [
        ("enter", "activate", "Confirm"),
        ("escape", "cancel", "Cancel"),
        ("up", "focus_prev", "Prev"),
        ("down", "focus_next", "Next"),
    ]

    def __init__(self, *, slot_index: int, slot_name: str) -> None:
        super().__init__()
        self.slot_index = slot_index
        self.slot_name = slot_name

    def compose(self) -> ComposeResult:
        """Build the overwrite modal layout."""

        with Vertical(classes="panel"):
            yield Static(f"Overwrite Slot {self.slot_index}?")
            yield Static(f'This will replace "{self.slot_name}".')
            self.confirm_button = Button("Confirm", id="confirm")
            self.cancel_button = Button("Cancel", id="cancel")
            yield self.confirm_button
            yield self.cancel_button

    def on_mount(self) -> None:
        """Focus the confirm button."""

        self.confirm_button.focus()

    def action_cancel(self) -> None:
        """Cancel overwrite and close the modal."""

        self.dismiss(result=False)

    def action_activate(self) -> None:
        """Activate the focused button."""

        focused = self.app.focused
        if isinstance(focused, Button) and not focused.disabled:
            focused.press()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle confirm and cancel actions."""

        if event.button.id == "confirm":
            self.dismiss(result=True)
        elif event.button.id == "cancel":
            self.dismiss(result=False)

    def action_focus_next(self) -> None:
        """Move focus to the next modal action."""

        self._move_focus(1)

    def action_focus_prev(self) -> None:
        """Move focus to the previous modal action."""

        self._move_focus(-1)

    def _move_focus(self, delta: int) -> None:
        """Cycle focus across modal action buttons."""

        focus_order = [self.confirm_button, self.cancel_button]
        focused = self.app.focused
        if focused not in focus_order:
            focus_order[0].focus()
            return
        index = focus_order.index(focused)
        focus_order[(index + delta) % len(focus_order)].focus()
