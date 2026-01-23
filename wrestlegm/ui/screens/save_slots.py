"""Save slot selection and naming screens."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Footer, Input, ListItem, ListView, Static

from wrestlegm import persistence

from ..widgets.list_views import FilteredListView


class SaveSlotSelectionScreen(Screen):
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

    def compose(self) -> ComposeResult:
        """Build the save slot selection layout."""

        title = "Load Game" if self.mode == "load" else "New Game"
        yield Static("WrestleGM", classes="section-title")
        yield Static(title, classes="section-title")
        self.menu = FilteredListView(
            is_item_active=self._is_item_active,
        )
        yield self.menu
        yield Footer()

    def on_mount(self) -> None:
        """Load slots and focus the list."""

        self.refresh_view()
        self.menu.focus()
        if self.menu.index is None and self.menu.children:
            first_active = self._first_active_index()
            if first_active is not None:
                self.menu.index = first_active
            elif self.mode != "load":
                self.menu.index = 0

    def _first_active_index(self) -> int | None:
        """Return the first selectable row index."""

        for index, item in enumerate(self.menu.children):
            if self._is_item_active(item):
                return index
        return None

    def refresh_view(self) -> None:
        """Reload slot metadata and rebuild the list."""

        self.slots = self.app.session.list_slots()
        if hasattr(self.menu, "clear"):
            self.menu.clear()
        else:
            for child in list(self.menu.children):
                child.remove()
        for slot in self.slots:
            label = self._slot_label(slot)
            self.menu.append(ListItem(Static(label), id=f"slot-{slot.slot_index}"))

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

    def _is_item_active(self, item: ListItem) -> bool:
        """Return whether a list item is selectable in the current mode."""

        if self.mode != "load":
            return True
        slot = self._slot_for_item(item)
        return slot.exists if slot else False

    def _slot_for_item(self, item: ListItem) -> persistence.SaveSlotInfo | None:
        """Map a list item back to slot metadata."""

        if item.id is None:
            return None
        try:
            slot_index = int(item.id.replace("slot-", ""))
        except ValueError:
            return None
        for slot in self.slots:
            if slot.slot_index == slot_index:
                return slot
        return None

    def action_select(self) -> None:
        """Handle selection based on mode and slot state."""

        if self.menu.index is None:
            return
        item = self.menu.children[self.menu.index]
        slot = self._slot_for_item(item)
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

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle list selection events."""

        if event.list_view is not self.menu:
            return
        self.action_select()

    def action_focus_next(self) -> None:
        """Move focus down the slot list."""

        self.menu.action_cursor_down()

    def action_focus_prev(self) -> None:
        """Move focus up the slot list."""

        self.menu.action_cursor_up()

    def action_back(self) -> None:
        """Return to the main menu."""

        from .main_menu import MainMenuScreen

        self.app.switch_screen(MainMenuScreen())


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

        from textual.containers import Vertical

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

        from textual.containers import Vertical

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
