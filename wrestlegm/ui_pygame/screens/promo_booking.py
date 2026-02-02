"""Promo booking screen for selecting a single wrestler for a promo slot."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

import pygame
import pygame_gui
from pygame.rect import Rect
from pygame_gui.elements import UIButton, UILabel

from wrestlegm.models import Promo
from wrestlegm.ui.drafts import PromoDraft

from .base import BaseScreen


def format_money(amount: int) -> str:
    """Format money amount as string (plain text for pygame)."""
    if amount < 0:
        return f"-${abs(amount):,}"
    return f"${amount:,}"


if TYPE_CHECKING:
    from wrestlegm.ui_pygame.app import WrestleGMApp
    from wrestlegm.ui_pygame.router import Router


class PromoBookingScreen(BaseScreen):
    """Book a promo with a single wrestler."""

    def __init__(
        self,
        app: "WrestleGMApp",
        router: "Router",
        slot_index: int = 0,
        existing_promo: Optional[Promo] = None,
    ) -> None:
        super().__init__(app, router)
        self._slot_index = slot_index
        self._draft = PromoDraft()
        if existing_promo:
            self._draft.wrestler_id = existing_promo.wrestler_id

        # UI elements
        self._title_label: Optional[UILabel] = None
        self._money_label: Optional[UILabel] = None
        self._wrestler_info_label: Optional[UILabel] = None
        self._mic_skill_label: Optional[UILabel] = None
        self._cost_label: Optional[UILabel] = None
        self._select_button: Optional[UIButton] = None
        self._cancel_button: Optional[UIButton] = None
        self._clear_button: Optional[UIButton] = None
        self._confirm_button: Optional[UIButton] = None
        self._on_select_callback: Optional[Callable] = None

    def _build_header(self, manager, rect) -> None:
        """Build header with title and money info."""
        from ..constants import FONT_SIZE_HEADER

        # Title
        slot_num = sum(
            1
            for i in range(self._slot_index + 1)
            if self._app.state.slot_type(i) == "promo"
        )
        title_text = f"Promo {slot_num}"
        title_rect = Rect(rect.x + 10, rect.y + 10, rect.width // 2, 30)
        self._title_label = UILabel(
            relative_rect=title_rect,
            text=title_text,
            manager=manager,
        )

        # Money
        money_rect = Rect(
            rect.x + rect.width // 2, rect.y + 10, rect.width // 2 - 10, 30
        )
        money_text = f"Money: {format_money(self._app.state.money)}"
        self._money_label = UILabel(
            relative_rect=money_rect,
            text=money_text,
            manager=manager,
        )

    def _build_body(self, manager, rect) -> None:
        """Build body with single wrestler selection slot."""
        from ..constants import MARGIN, PADDING, FONT_SIZE_BODY

        # Wrestler selection area
        slot_height = 100
        slot_rect = Rect(
            rect.x + MARGIN,
            rect.y + PADDING,
            rect.width - (MARGIN * 2),
            slot_height,
        )

        if self._draft.wrestler_id:
            # Show selected wrestler info
            self._show_wrestler_info(manager, slot_rect)
        else:
            # Show "SELECT WRESTLER" button
            self._select_button = UIButton(
                relative_rect=slot_rect,
                text="SELECT WRESTLER",
                manager=manager,
            )

    def _show_wrestler_info(self, manager, rect: Rect) -> None:
        """Display wrestler info when selected."""
        wrestler_id = self._draft.wrestler_id
        if not wrestler_id:
            return

        wrestler = self._app.state.roster.get(wrestler_id)
        if not wrestler:
            return

        # Wrestler name
        name_rect = Rect(rect.x + 10, rect.y + 10, rect.width - 20, 25)
        self._wrestler_info_label = UILabel(
            relative_rect=name_rect,
            text=wrestler.name,
            manager=manager,
        )

        # Mic skill
        mic_rect = Rect(rect.x + 10, rect.y + 40, rect.width // 2 - 15, 20)
        self._mic_skill_label = UILabel(
            relative_rect=mic_rect,
            text=f"Mic Skill: {wrestler.mic_skill}",
            manager=manager,
        )

        # Cost
        cost = self._app.state.wrestler_booking_price(wrestler_id)
        cost_rect = Rect(
            rect.x + rect.width // 2 + 5, rect.y + 40, rect.width // 2 - 15, 20
        )
        self._cost_label = UILabel(
            relative_rect=cost_rect,
            text=f"Cost: {format_money(cost)}",
            manager=manager,
        )

        # Change button
        change_rect = Rect(rect.x + 10, rect.y + 70, rect.width - 20, 25)
        self._select_button = UIButton(
            relative_rect=change_rect,
            text="CHANGE WRESTLER",
            manager=manager,
        )

    def _build_actions(self, manager, rect) -> None:
        """Build actions bar with Cancel, Clear Slot, and Confirm buttons."""
        from ..constants import MARGIN, PADDING

        button_height = 50
        button_width = 120
        button_y = rect.y + (rect.height - button_height) // 2

        # Cancel button (left)
        cancel_rect = Rect(rect.x + MARGIN, button_y, button_width, button_height)
        self._cancel_button = UIButton(
            relative_rect=cancel_rect,
            text="CANCEL",
            manager=manager,
        )

        # Clear Slot button (center) - only if there's an existing slot
        existing = self._app.state.show_card[self._slot_index]
        clear_x = rect.x + (rect.width - button_width) // 2
        clear_rect = Rect(clear_x, button_y, button_width, button_height)
        self._clear_button = UIButton(
            relative_rect=clear_rect,
            text="CLEAR SLOT",
            manager=manager,
        )
        self._clear_button.disable() if existing is None else None

        # Confirm button (right)
        confirm_rect = Rect(
            rect.x + rect.width - button_width - MARGIN,
            button_y,
            button_width,
            button_height,
        )
        self._confirm_button = UIButton(
            relative_rect=confirm_rect,
            text="CONFIRM",
            manager=manager,
        )

        # Update confirm button state based on validation
        self._update_confirm_button()

    def _build_footer(self, manager, rect) -> None:
        """Build footer with hints."""
        hint_rect = Rect(rect.x + 10, rect.y + 5, rect.width - 20, 20)
        UILabel(
            relative_rect=hint_rect,
            text="Select a wrestler to book this promo",
            manager=manager,
        )

    def _update_confirm_button(self) -> None:
        """Update confirm button based on validation."""
        if not self._confirm_button:
            return

        errors = self._validate_draft()
        if errors:
            self._confirm_button.disable()
        else:
            self._confirm_button.enable()

    def _validate_draft(self) -> list[str]:
        """Validate the current draft."""
        if not self._draft.is_complete():
            return ["incomplete"]

        wrestler_id = self._draft.wrestler_id
        if not wrestler_id:
            return ["no_wrestler"]

        wrestler = self._app.state.roster.get(wrestler_id)
        if wrestler is None:
            return ["unknown_wrestler"]

        promo = Promo(wrestler=wrestler)
        return self._app.state.validate_promo(promo, slot_index=self._slot_index)

    def _rebuild_body(self) -> None:
        """Rebuild body section with updated wrestler selection.

        Called when a wrestler is selected to refresh the UI without navigation.
        Clears existing body elements and recreates them.
        """
        manager = getattr(self._app, "ui_manager", None)
        if not manager:
            return

        # Get body zone rect
        zones = self._compute_zones(pygame.display.get_surface().get_rect())
        body_rect = zones["body"]

        # Kill existing body UI elements
        if self._wrestler_info_label:
            self._wrestler_info_label.kill()
            self._wrestler_info_label = None
        if self._mic_skill_label:
            self._mic_skill_label.kill()
            self._mic_skill_label = None
        if self._cost_label:
            self._cost_label.kill()
            self._cost_label = None
        if self._select_button:
            self._select_button.kill()
            self._select_button = None

        # Rebuild body
        self._build_body(manager, body_rect)

    def _set_wrestler(self, wrestler_id: str) -> None:
        """Set the selected wrestler."""
        self._draft.wrestler_id = wrestler_id
        # Rebuild UI to show wrestler info
        self._rebuild_body()

    def _get_promo_from_draft(self) -> Optional[Promo]:
        """Get a Promo object from current draft if complete."""
        if not self._draft.wrestler_id:
            return None
        wrestler = self._app.state.roster.get(self._draft.wrestler_id)
        if wrestler:
            return Promo(wrestler=wrestler)
        return None

    def _on_select_wrestler(self) -> None:
        """Navigate to wrestler selection screen."""
        # Get already booked wrestlers (excluding this slot)
        booked_ids: set[str] = set()
        for index, slot in enumerate(self._app.state.show_card):
            if slot is None or index == self._slot_index:
                continue
            from wrestlegm.models import Match

            if isinstance(slot, Match):
                booked_ids.update(slot.wrestler_ids)
            else:
                booked_ids.add(slot.wrestler_id)

        self._router.navigate(
            "wrestler_selection",
            slot_index=self._slot_index,
            title=f"Select Wrestler for Promo",
            current_ids=set(),
            booked_ids=booked_ids,
            on_select=lambda w: self._set_wrestler(w),
            allow_low_stamina=True,
        )

    def _on_cancel(self) -> None:
        """Return to booking hub without saving."""
        self._router.back()

    def _on_clear(self) -> None:
        """Clear the slot and return to booking hub."""
        from ..modals import ConfirmModal

        existing = self._app.state.show_card[self._slot_index]
        if existing is None:
            return

        # Show confirmation modal
        parent_rect = self._get_screen_rect()
        confirm_modal = ConfirmModal(
            self._app,
            self._app.ui_manager,
            parent_rect,
            title="Clear Slot",
            message="Are you sure you want to clear this promo slot?",
            on_confirm=self._do_clear,
            on_cancel=None,
            confirm_text="Yes",
            cancel_text="No",
        )
        confirm_modal.show()

    def _do_clear(self) -> None:
        """Actually clear the slot."""
        self._app.state.clear_slot(self._slot_index)
        self._router.back()

    def _on_confirm(self) -> None:
        """Save the promo and return to booking hub."""
        if self._validate_draft():
            return

        wrestler_id = self._draft.wrestler_id
        if not wrestler_id:
            return

        wrestler = self._app.state.roster.get(wrestler_id)
        if wrestler is None:
            return

        promo = Promo(wrestler=wrestler)
        self._app.state.set_slot(self._slot_index, promo)
        self._router.back()

    def _get_screen_rect(self) -> Rect:
        """Get the current screen rectangle."""
        zones = self._compute_zones(pygame.display.get_surface().get_rect())
        return zones["body"]

    def handle_event(self, event) -> bool:
        """Handle pygame events."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self._select_button:
                self._on_select_wrestler()
                return True
            elif event.ui_element == self._cancel_button:
                self._on_cancel()
                return True
            elif event.ui_element == self._clear_button:
                self._on_clear()
                return True
            elif event.ui_element == self._confirm_button:
                self._on_confirm()
                return True
        return False

    def update(self, time_delta: float) -> None:
        """Update screen state."""
        pass
