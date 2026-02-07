"""Booking hub screen for show card management."""

from __future__ import annotations

from pygame.rect import Rect
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIButton, UILabel, UIPanel

from wrestlegm import constants
from wrestlegm.models import Match, MATCH_CATEGORIES
from wrestlegm.ui_pygame.screens.base import BaseScreen
from wrestlegm.ui_pygame.constants import (
    MARGIN,
    PADDING,
)


class BookingHubScreen(BaseScreen):
    """Show overview and booking hub for the current card.

    Responsibilities:
    - Display the current show number and slot summaries.
    - Allow the user to open a slot editor.
    - Gate Run Show based on validation.
    """

    def __init__(self, app, router) -> None:
        super().__init__(app, router)
        self._title_label: UILabel | None = None
        self._cost_label: UILabel | None = None
        self._money_label: UILabel | None = None
        self._slot_buttons: list[UIButton] = []
        self._back_button: UIButton | None = None
        self._run_button: UIButton | None = None
        self._show_header_label: UILabel | None = None

    def _build_header(self, manager, rect: Rect) -> None:
        """Build header with title, show cost, and money."""
        # Title on the left
        title_rect = Rect(
            rect.x + MARGIN,
            rect.y + PADDING,
            rect.width // 3 - MARGIN * 2,
            rect.height - PADDING * 2,
        )
        self._title_label = UILabel(
            relative_rect=title_rect,
            text="BOOKING HUB",
            manager=manager,
            object_id=ObjectID(
                class_id="@header_title", object_id="#booking_hub_title"
            ),
        )

        # Show cost in the middle
        cost = self._app.state.current_show_cost()
        cost_text = f"Cost: ${cost:,}"
        cost_rect = Rect(
            rect.x + rect.width // 3,
            rect.y + PADDING,
            rect.width // 3 - MARGIN * 2,
            rect.height - PADDING * 2,
        )
        self._cost_label = UILabel(
            relative_rect=cost_rect,
            text=cost_text,
            manager=manager,
            object_id=ObjectID(class_id="@header_stat", object_id="#booking_hub_cost"),
        )

        # Money on the right
        money_text = self._format_money(self._app.state.money)
        money_rect = Rect(
            rect.x + 2 * rect.width // 3,
            rect.y + PADDING,
            rect.width // 3 - MARGIN * 2,
            rect.height - PADDING * 2,
        )
        self._money_label = UILabel(
            relative_rect=money_rect,
            text=money_text,
            manager=manager,
            object_id=ObjectID(class_id="@money_label", object_id="#booking_hub_money"),
        )

    def _build_body(self, manager, rect: Rect) -> None:
        """Build body with 5 slot buttons."""
        # Show number header
        header_rect = Rect(
            rect.x + MARGIN,
            rect.y,
            rect.width - MARGIN * 2,
            30,
        )
        show_index = self._app.state.show_index
        self._show_header_label = UILabel(
            relative_rect=header_rect,
            text=f"Show #{show_index}",
            manager=manager,
            object_id=ObjectID(
                class_id="@section_title", object_id="#booking_hub_show_header"
            ),
        )

        # Slot buttons
        slot_height = (rect.height - 40 - PADDING * 2) // constants.SHOW_SLOT_COUNT
        slot_spacing = 8
        self._slot_buttons = []

        for index in range(constants.SHOW_SLOT_COUNT):
            slot_rect = Rect(
                rect.x + MARGIN,
                rect.y + 40 + index * (slot_height + slot_spacing),
                rect.width - MARGIN * 2,
                slot_height,
            )
            slot_text = self._get_slot_text(index)
            button = UIButton(
                relative_rect=slot_rect,
                text=slot_text,
                manager=manager,
                object_id=ObjectID(
                    class_id="@booking_slot_button",
                    object_id=f"#booking_slot_{index + 1}",
                ),
            )
            # Store slot index on the button for reference
            button.slot_index = index
            self._slot_buttons.append(button)

    def _build_actions(self, manager, rect: Rect) -> None:
        """Build action buttons (Back and Run Show)."""
        button_width = 120
        button_height = 50
        button_y = rect.y + (rect.height - button_height) // 2

        # Back button (left)
        back_rect = Rect(
            rect.x + MARGIN,
            button_y,
            button_width,
            button_height,
        )
        self._back_button = UIButton(
            relative_rect=back_rect,
            text="BACK",
            manager=manager,
            object_id=ObjectID(
                class_id="@secondary_button", object_id="#booking_hub_back"
            ),
        )

        # Run Show button (right)
        run_rect = Rect(
            rect.x + rect.width - button_width - MARGIN,
            button_y,
            button_width,
            button_height,
        )
        # Check if show is valid
        errors = self._app.state.validate_show()
        is_valid = not bool(errors)

        self._run_button = UIButton(
            relative_rect=run_rect,
            text="RUN SHOW",
            manager=manager,
            object_id=ObjectID(
                class_id="@primary_button", object_id="#booking_hub_run_show"
            ),
        )
        if not is_valid:
            self._run_button.disable()

    def _build_footer(self, manager, rect: Rect) -> None:
        """Build footer with hint text."""
        footer_rect = Rect(
            rect.x + MARGIN,
            rect.y,
            rect.width - MARGIN * 2,
            rect.height,
        )
        UILabel(
            relative_rect=footer_rect,
            text="Click a slot to book · Fill all slots to run show",
            manager=manager,
            object_id=ObjectID(class_id="@footer_hint", object_id="#booking_hub_hint"),
        )

    def update(self, time_delta: float) -> None:
        """Update slot text and button states."""
        # Update cost label
        if self._cost_label:
            cost = self._app.state.current_show_cost()
            self._cost_label.set_text(f"Cost: ${cost:,}")

        # Update money label
        if self._money_label:
            money_text = self._format_money(self._app.state.money)
            self._money_label.set_text(money_text)

        # Update slot buttons
        for index, button in enumerate(self._slot_buttons):
            if button:
                slot_text = self._get_slot_text(index)
                button.set_text(slot_text)

        # Update Run Show button state
        if self._run_button:
            errors = self._app.state.validate_show()
            is_valid = not bool(errors)
            if is_valid:
                self._run_button.enable()
            else:
                self._run_button.disable()

    def handle_event(self, event) -> bool:
        """Handle button presses."""
        import pygame_gui

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # Check slot buttons
            for button in self._slot_buttons:
                if event.ui_element == button:
                    slot_index = button.slot_index
                    self._on_slot_clicked(slot_index)
                    return True

            # Check action buttons
            if event.ui_element == self._back_button:
                self._on_back()
                return True
            elif event.ui_element == self._run_button:
                self._on_run_show()
                return True

        return False

    def _get_slot_text(self, index: int) -> str:
        """Get the display text for a slot."""
        slot = self._app.state.show_card[index]
        slot_type = self._app.state.slot_type(index)
        label = self._slot_label(index, slot_type)

        if slot is None:
            return f"{label}\n[ EMPTY ]"

        if isinstance(slot, Match):
            wrestlers = [self._app.state.roster[w_id] for w_id in slot.wrestler_ids]
            match_type = self._app.state.match_types.get(slot.match_type_id)
            match_type_name = match_type.name if match_type else "Unknown"
            category_name = (
                slot.match_category.name if slot.match_category else "Unknown"
            )

            # Calculate match cost
            match_cost = self._app.state.match_type_base_cost(slot.match_type_id)
            match_cost += sum(
                self._app.state.wrestler_booking_price(w_id)
                for w_id in slot.wrestler_ids
            )

            # Get wrestler names
            wrestler_names = " vs ".join(w.name for w in wrestlers)

            return f"{label} · {category_name} · ${match_cost:,}\n{wrestler_names}\n{match_type_name}"
        else:
            # Promo
            wrestler = self._app.state.roster[slot.wrestler_id]
            promo_cost = self._app.state.wrestler_booking_price(wrestler.id)
            return f"{label} · ${promo_cost:,}\n{wrestler.name}"

    def _slot_label(self, slot_index: int, slot_type: str) -> str:
        """Return the label for a slot index and type."""
        count = sum(
            1
            for index in range(slot_index + 1)
            if constants.SHOW_SLOT_TYPES[index] == slot_type
        )
        return f"{slot_type.title()} {count}"

    def _on_slot_clicked(self, slot_index: int) -> None:
        """Navigate to match or promo booking."""
        slot_type = self._app.state.slot_type(slot_index)

        if slot_type == "match":
            # Get existing match category or default to first
            existing = self._app.state.show_card[slot_index]
            if isinstance(existing, Match):
                match_category = existing.match_category
            else:
                match_category = sorted(MATCH_CATEGORIES, key=lambda item: item.id)[0]

            self._router.navigate(
                "match_booking",
                slot_index=slot_index,
                match_category=match_category,
            )
        else:
            # Promo slot
            self._router.navigate("promo_booking", slot_index=slot_index)

    def _on_back(self) -> None:
        """Return to game hub."""
        self._router.back()

    def _on_run_show(self) -> None:
        """Run the show with debt confirmation if needed."""
        # Check if show is valid
        errors = self._app.state.validate_show()
        if errors:
            return

        show_cost = self._app.state.current_show_cost()
        will_debt = show_cost > self._app.state.money

        if will_debt:
            # Show debt warning modal via router
            self._router.show_confirm(
                title="Confirm Run Show",
                message=f"Show cost (${show_cost:,}) exceeds your money (${self._app.state.money:,}).\n\nYou will go into debt. Continue?",
                on_confirm=lambda: self._router.navigate("simulating"),
                on_cancel=None,  # Stay on booking hub
                confirm_text="Yes",
                cancel_text="No",
            )
        else:
            # No debt, proceed directly
            self._router.navigate("simulating")

    def _format_money(self, amount: int) -> str:
        """Format money for display."""
        if amount < 0:
            return f"-${abs(amount):,}"
        return f"${amount:,}"
