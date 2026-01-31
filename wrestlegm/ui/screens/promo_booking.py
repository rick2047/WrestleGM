"""Promo booking screen."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, ListItem, ListView, Static

from wrestlegm.models import Match, Promo

from ..drafts import PromoDraft
from ..formatting import format_money, slot_label
from ..widgets.list_views import EdgeAwareListView
from ..widgets.wrestler_view import WrestlerView, WrestlerViewConfig, build_wrestler_view_data
from .modals import ConfirmBookingModal
from .standard import StandardScreen
from .wrestler_selection import WrestlerSelectionScreen


class PromoBookingScreen(StandardScreen):
    """Editor for a single promo slot."""

    BINDINGS = [
        ("enter", "select_field", "Select"),
        ("up", "focus_prev", "Prev"),
        ("down", "focus_next", "Next"),
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, slot_index: int) -> None:
        super().__init__()
        self.slot_index = slot_index
        self.draft = PromoDraft()

    def header_title(self) -> str:
        return slot_label(self.slot_index, "promo")

    def header_right(self) -> str:
        return f"Money: {format_money(self.app.state.money)}"

    def compose_body(self) -> ComposeResult:
        with Vertical(classes="booking-shell"):
            with Vertical(classes="booking-card"):
                yield Static("Performer", classes="booking-section-title")

                config = WrestlerViewConfig(
                    show_avatar=True,
                    show_name=True,
                    show_stats=True,
                    show_description=False,
                    show_rivalry=False,
                )
                self.wrestler_view = WrestlerView(None, config)
                self.fields = EdgeAwareListView(
                    ListItem(self.wrestler_view, id="field-wrestler"),
                    on_edge_prev=self.action_focus_prev,
                    on_edge_next=self.action_focus_next,
                )
                self.fields.add_class("match-wrestlers-scroll")
                yield self.fields

    def compose_actions(self) -> list[Button]:
        self.clear_button = Button("Clear Slot", id="clear")
        self.confirm_button = Button("Confirm", id="confirm")
        self.cancel_button = Button("Cancel", id="cancel")
        return [self.clear_button, self.confirm_button, self.cancel_button]

    def on_mount(self) -> None:
        super().on_mount()
        self.add_class("booking-screen")
        self.fields.focus()
        existing = self.app.state.show_card[self.slot_index]
        if isinstance(existing, Promo):
            self.draft.wrestler_id = existing.wrestler_id
        self.refresh_view()

    def refresh_view(self) -> None:
        wrestler_view = (
            build_wrestler_view_data(self.app.state, self.draft.wrestler_id)
            if self.draft.wrestler_id
            else None
        )
        self.wrestler_view.set_wrestler(wrestler_view, rivalries=[])
        self.confirm_button.disabled = not self.draft.is_complete() or bool(
            self.validate_draft()
        )
        self.clear_button.disabled = self.app.state.show_card[self.slot_index] is None
        self.update_header()

    def validate_draft(self) -> list[str]:
        if not self.draft.is_complete():
            return ["incomplete"]
        wrestler_id = self.draft.wrestler_id or ""
        wrestler = self.app.state.roster.get(wrestler_id)
        if wrestler is None:
            return ["unknown_wrestler"]
        return self.app.state.validate_promo(
            Promo(wrestler=wrestler),
            slot_index=self.slot_index,
        )

    def action_select_field(self) -> None:
        title = f"Select Wrestler ({slot_label(self.slot_index, 'promo')})"
        self.app.push_screen(
            WrestlerSelectionScreen(
                slot_index=self.slot_index,
                title=title,
                current_ids=set(),
                booked_ids=self._booked_ids(),
                on_select=self.set_wrestler,
                allow_low_stamina=True,
            )
        )

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle selection from the field list."""

        if event.list_view is not self.fields:
            return
        self.action_select_field()

    def set_wrestler(self, wrestler_id: str) -> None:
        self.draft.wrestler_id = wrestler_id
        self.refresh_view()

    def action_cancel(self) -> None:
        self.app.pop_screen()

    def action_focus_next(self) -> None:
        self._move_focus(1)

    def action_focus_prev(self) -> None:
        self._move_focus(-1)

    def _move_focus(self, delta: int) -> None:
        focus_order = [self.fields, self.confirm_button, self.clear_button, self.cancel_button]
        focused = self.app.focused
        if focused not in focus_order:
            focus_order[0].focus()
            return
        index = focus_order.index(focused)
        next_index = index
        for _ in range(len(focus_order)):
            next_index = (next_index + delta) % len(focus_order)
            candidate = focus_order[next_index]
            if candidate is self.fields or not candidate.disabled:
                if candidate is self.fields and focused is not self.fields:
                    self.fields.index = 0
                candidate.focus()
                return

    def action_clear(self) -> None:
        if self.app.state.show_card[self.slot_index] is None:
            return
        self.app.state.clear_slot(self.slot_index)
        self.app.pop_screen()

    def action_confirm(self) -> None:
        if self.confirm_button.disabled:
            return
        self.app.push_screen(ConfirmBookingModal(), self.handle_confirmation)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            self.action_confirm()
        elif event.button.id == "clear":
            self.action_clear()
        elif event.button.id == "cancel":
            self.action_cancel()

    def on_screen_resume(self) -> None:
        super().on_screen_resume()
        self.refresh_view()

    def handle_confirmation(self, result: bool | None) -> None:
        if result:
            self.commit_booking()

    def commit_booking(self) -> None:
        wrestler_id = self.draft.wrestler_id or ""
        wrestler = self.app.state.roster.get(wrestler_id)
        if wrestler is None:
            return
        promo = Promo(wrestler=wrestler)
        self.app.state.set_slot(self.slot_index, promo)
        self.app.pop_screen()

    def _booked_ids(self) -> set[str]:
        booked: set[str] = set()
        for index, slot in enumerate(self.app.state.show_card):
            if slot is None or index == self.slot_index:
                continue
            if isinstance(slot, Match):
                booked.update(slot.wrestler_ids)
            else:
                booked.add(slot.wrestler_id)
        if self.draft.wrestler_id:
            booked.add(self.draft.wrestler_id)
        return booked
