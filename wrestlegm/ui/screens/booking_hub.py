"""Show overview and booking hub for the current card."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Button, Static

from wrestlegm import constants
from wrestlegm.models import Match

from ..formatting import (
    build_match_participants,
    build_name_cell,
    format_money,
    match_category_label,
    slot_label,
)
from ..routes import (
    GAME_HUB,
    MATCH_BOOKING,
    PROMO_BOOKING,
    SIMULATING,
)
from .standard import StandardScreen
from .modals import ConfirmRunShowModal


class BookingHubScreen(StandardScreen):
    """Show overview and booking hub for the current card.

    Responsibilities:
    - Display the current show number and slot summaries.
    - Allow the user to open a slot editor.
    - Gate Run Show based on validation.
    """

    BINDINGS = [
        ("enter", "select", "Select"),
        ("r", "run_show", "Run Show"),
        ("up", "focus_prev", "Prev"),
        ("down", "focus_next", "Next"),
        ("escape", "back", "Back"),
    ]

    TITLE = "Booking Hub"

    def header_left(self) -> str:
        return f"Money: {format_money(self.app.state.money)}"

    def header_right(self) -> str:
        cost = self.app.state.current_show_cost()
        return f"Cost: {format_money(cost)}"

    def compose_body(self) -> ComposeResult:
        """Build the booking hub layout."""

        self.show_header = Static("", classes="section-title")
        yield self.show_header

        self.slot_buttons: list[Button] = []
        with VerticalScroll(classes="booking-slot-scroll"):
            with Vertical(classes="booking-slot-group"):
                for index in range(constants.SHOW_SLOT_COUNT):
                    button = Button("", id=f"slot-button-{index}", classes="booking-slot-button")
                    self.slot_buttons.append(button)
                    yield button

    def compose_actions(self) -> list[Button]:
        self.run_button = Button("Run Show", id="run-show")
        self.run_button.disabled = True
        self.back_button = Button("Back", id="back")
        return [self.run_button, self.back_button]

    def on_mount(self) -> None:
        """Focus the first slot and refresh the view."""

        super().on_mount()
        self.refresh_view()
        if self.slot_buttons:
            self.slot_buttons[0].focus()

    def refresh_view(self) -> None:
        """Update slot text and Run Show enablement."""

        summary = self.app.state.rivalry_manager.rivalry_and_cooldown_summary_for_card(
            [slot for slot in self.app.state.show_card if slot is not None]
        )
        if summary:
            self.show_header.update(f"Show #{self.app.state.show_index}\n{summary}")
        else:
            self.show_header.update(f"Show #{self.app.state.show_index}")
        for index, button in enumerate(self.slot_buttons):
            button.label = self.slot_text(index)
        self.run_button.disabled = bool(self.app.state.validate_show())
        self.update_header()

    def slot_text(self, index: int) -> str:
        """Render the slot summary text for a match slot."""

        slot = self.app.state.show_card[index]
        slot_type = self.app.state.slot_type(index)
        label = slot_label(index, slot_type)
        if slot is None:
            return f"{label}\n[ Empty ]"
        if isinstance(slot, Match):
            wrestlers = [self.app.state.roster[w_id] for w_id in slot.wrestler_ids]
            match_type = self.app.state.match_types.get(slot.match_type_id)
            match_type_name = match_type.name if match_type else "Unknown"
            category_name = match_category_label(slot.match_category_id)
            emojis = self.app.state.rivalry_emojis_for_match(slot.wrestler_ids)
            match_cost = match_type.base_cost if match_type else 0
            label_text = f"{label} · {category_name} · ${match_cost:,}"
            if emojis:
                label_text = f"{label_text}  {emojis}"
            return (
                f"{label_text}\n{build_match_participants(wrestlers)}\n"
                f"{category_name} · {match_type_name}"
            )
        wrestler = self.app.state.roster[slot.wrestler_id]
        return f"{label}\n{build_name_cell(wrestler.name, wrestler.alignment)}"

    def action_select(self) -> None:
        """Open the booking screen for the selected slot."""

        focused = self.app.focused
        if isinstance(focused, Button) and focused.id:
            self._handle_selection(focused.id)
            return
        if self.slot_buttons:
            self._handle_selection(self.slot_buttons[0].id)

    def open_match_booking(self, slot_index: int) -> None:
        """Open match booking with the existing or default category."""

        existing = self.app.state.show_card[slot_index]
        if isinstance(existing, Match):
            match_category_id = existing.match_category_id
        else:
            match_category_id = constants.MATCH_CATEGORY_ORDER[0]
        self.app.navigate(
            MATCH_BOOKING,
            slot_index=slot_index,
            match_category_id=match_category_id,
        )

    def action_run_show(self) -> None:
        """Run the show if the current card is valid."""

        if self.app.state.validate_show():
            return
        show_cost = self.app.state.current_show_cost()
        will_debt = show_cost > self.app.state.money

        def _handle_confirm(result: bool | None) -> None:
            if result:
                self.app.navigate(SIMULATING)

        self.app.push_screen(
            ConfirmRunShowModal(
                money=self.app.state.money,
                show_cost=show_cost,
                will_debt=will_debt,
            ),
            _handle_confirm,
        )

    def action_back(self) -> None:
        """Return to the game hub."""

        self.app.navigate(GAME_HUB)

    def action_focus_next(self) -> None:
        """Move focus to the next booking hub control."""

        self._move_focus(1)

    def action_focus_prev(self) -> None:
        """Move focus to the previous booking hub control."""

        self._move_focus(-1)

    def _move_focus(self, delta: int) -> None:
        """Cycle focus between the slot list and action buttons."""

        focus_order = [*self.slot_buttons, self.run_button, self.back_button]
        focused = self.app.focused
        if focused not in focus_order:
            if self.slot_buttons:
                self.slot_buttons[0].focus()
            return
        index = focus_order.index(focused)
        next_index = index
        for _ in range(len(focus_order)):
            next_index = (next_index + delta) % len(focus_order)
            candidate = focus_order[next_index]
            if candidate is self.run_button and candidate.disabled:
                continue
            candidate.focus()
            return

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle booking hub button presses."""

        if event.button.id == "run-show":
            self.action_run_show()
        elif event.button.id == "back":
            self.action_back()
        else:
            self._handle_selection(event.button.id)

    def _handle_selection(self, button_id: str | None) -> None:
        if not button_id:
            return
        if button_id.startswith("slot-button-"):
            try:
                index = int(button_id.replace("slot-button-", ""))
            except ValueError:
                return
            if self.app.state.slot_type(index) == "match":
                self.open_match_booking(index)
            else:
                self.app.navigate(PROMO_BOOKING, slot_index=index)

    def on_screen_resume(self) -> None:
        """Refresh slot details after returning to the hub."""

        super().on_screen_resume()
        self.refresh_view()
