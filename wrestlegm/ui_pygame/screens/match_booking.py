"""Match booking screen with category/type selectors and wrestler slots."""

from __future__ import annotations

from itertools import combinations
from typing import TYPE_CHECKING

import pygame
import pygame_gui
from pygame.rect import Rect
from pygame_gui.elements import UIButton, UIDropDownMenu, UILabel, UIPanel

from wrestlegm.models import MATCH_CATEGORIES, Match, MatchCategory

from .base import BaseScreen

if TYPE_CHECKING:
    pass


class MatchBookingScreen(BaseScreen):
    """Book a match with wrestlers and match type."""

    def __init__(
        self, app, router, slot_index: int = 0, existing_match: Match | None = None
    ):
        super().__init__(app, router)
        self._slot_index = slot_index
        self._match = existing_match
        self._draft_wrestler_ids: list[str | None] = []
        self._draft_category: MatchCategory | None = None
        self._draft_match_type_id: str | None = None
        self._category_dropdown: UIDropDownMenu | None = None
        self._type_dropdown: UIDropDownMenu | None = None
        self._wrestler_slot_buttons: list[UIButton] = []
        self._rivalry_labels: list[UILabel] = []
        self._slot_panels: list[UIPanel] = []
        self._cost_label: UILabel | None = None
        self._confirm_modal = None

    def build(self, manager, rect) -> None:
        """Build UI elements in the 4 zones."""
        zones = self._compute_zones(rect)

        # Initialize draft from existing match or defaults
        self._initialize_draft()

        self._build_header(manager, zones["header"])
        self._build_body(manager, zones["body"])
        self._build_actions(manager, zones["actions"])
        self._build_footer(manager, zones["footer"])

    def _initialize_draft(self) -> None:
        """Initialize draft state from existing match or defaults."""
        if self._match is not None:
            self._draft_category = self._match.match_category
            self._draft_match_type_id = self._match.match_type_id
            self._draft_wrestler_ids = list(self._match.wrestler_ids)
        else:
            # Default to Singles category
            self._draft_category = MATCH_CATEGORIES[0] if MATCH_CATEGORIES else None
            self._draft_match_type_id = None
            if self._draft_category:
                self._draft_wrestler_ids = [None] * self._draft_category.size

        # Set default match type if not set
        if self._draft_match_type_id is None and self._app.state.match_types:
            self._draft_match_type_id = next(iter(self._app.state.match_types.keys()))

    def _build_header(self, manager, rect) -> None:
        """Build header with title and money info."""
        # Title
        title_rect = Rect(rect.x + 8, rect.y + 10, rect.width - 16, 30)
        UILabel(
            relative_rect=title_rect,
            text=f"Book Match - Slot {self._slot_index + 1}",
            manager=manager,
        )

        # Money display
        money_rect = Rect(rect.x + rect.width - 120, rect.y + 10, 110, 30)
        UILabel(
            relative_rect=money_rect,
            text=f"${self._app.state.money:,}",
            manager=manager,
        )

    def _build_body(self, manager, rect) -> None:
        """Build body with category/type selectors and wrestler slots."""
        y_offset = rect.y + 8

        # Category selector
        category_label_rect = Rect(rect.x + 8, y_offset, 80, 24)
        UILabel(
            relative_rect=category_label_rect,
            text="Category:",
            manager=manager,
        )

        category_dropdown_rect = Rect(rect.x + 90, y_offset, 180, 32)
        category_options = [
            (f"{cat.size}v{cat.size} {cat.name}", str(cat.id))
            for cat in MATCH_CATEGORIES
        ]
        initial_category = str(self._draft_category.id) if self._draft_category else "1"
        self._category_dropdown = UIDropDownMenu(
            relative_rect=category_dropdown_rect,
            options_list=[opt[0] for opt in category_options],
            starting_option=next(
                (opt[0] for opt in category_options if opt[1] == initial_category),
                category_options[0][0],
            ),
            manager=manager,
        )
        self._category_dropdown.category_map = {
            opt[0]: int(opt[1]) for opt in category_options
        }

        # Type selector
        y_offset += 40
        type_label_rect = Rect(rect.x + 8, y_offset, 80, 24)
        UILabel(
            relative_rect=type_label_rect,
            text="Type:",
            manager=manager,
        )

        type_dropdown_rect = Rect(rect.x + 90, y_offset, 180, 32)
        match_type_options = self._get_match_type_options()
        initial_type = self._draft_match_type_id or (
            match_type_options[0][1] if match_type_options else ""
        )
        self._type_dropdown = UIDropDownMenu(
            relative_rect=type_dropdown_rect,
            options_list=[opt[0] for opt in match_type_options],
            starting_option=next(
                (opt[0] for opt in match_type_options if opt[1] == initial_type),
                match_type_options[0][0] if match_type_options else "",
            ),
            manager=manager,
        )
        self._type_dropdown.type_map = {opt[0]: opt[1] for opt in match_type_options}

        # Cost breakdown
        y_offset += 40
        cost_rect = Rect(rect.x + 8, y_offset, rect.width - 16, 24)
        self._cost_label = UILabel(
            relative_rect=cost_rect,
            text=self._get_cost_text(),
            manager=manager,
        )

        # Wrestler slots
        y_offset += 40
        slot_height = 70
        slot_spacing = 8

        self._wrestler_slot_buttons = []
        self._rivalry_labels = []
        self._slot_panels = []

        for i in range(self._get_required_wrestler_count()):
            # Slot panel
            slot_rect = Rect(
                rect.x + 8,
                y_offset + i * (slot_height + slot_spacing),
                rect.width - 16,
                slot_height,
            )
            slot_panel = UIPanel(
                relative_rect=slot_rect,
                manager=manager,
            )

            # Wrestler button
            wrestler_id = (
                self._draft_wrestler_ids[i]
                if i < len(self._draft_wrestler_ids)
                else None
            )
            wrestler = self._app.state.roster.get(wrestler_id) if wrestler_id else None

            button_text = wrestler.name if wrestler else "SELECT WRESTLER"
            button_rect = Rect(8, 10, slot_rect.width - 16, 36)
            button = UIButton(
                relative_rect=button_rect,
                text=button_text,
                manager=manager,
                container=slot_panel,
                object_id=f"wrestler_slot_{i}",
            )
            self._wrestler_slot_buttons.append(button)

            # Rivalry indicator
            rivalries = self._get_rivalry_badges_for_wrestler(wrestler_id)
            rivalry_text = " ".join(rivalries) if rivalries else ""
            rivalry_rect = Rect(8, 48, slot_rect.width - 16, 20)
            rivalry_label = UILabel(
                relative_rect=rivalry_rect,
                text=rivalry_text,
                manager=manager,
                container=slot_panel,
            )
            self._rivalry_labels.append(rivalry_label)
            self._slot_panels.append(slot_panel)

    def _build_actions(self, manager, rect) -> None:
        """Build action buttons."""
        button_width = 120
        button_height = 44
        button_y = rect.y + (rect.height - button_height) // 2

        # Cancel button
        cancel_rect = Rect(rect.x + 16, button_y, button_width, button_height)
        self._cancel_button = UIButton(
            relative_rect=cancel_rect,
            text="CANCEL",
            manager=manager,
        )

        # Clear Slot button
        clear_rect = Rect(
            rect.x + rect.width // 2 - button_width // 2,
            button_y,
            button_width,
            button_height,
        )
        self._clear_button = UIButton(
            relative_rect=clear_rect,
            text="CLEAR SLOT",
            manager=manager,
        )
        # Disable if no existing match
        if self._match is None:
            self._clear_button.disable()

        # Confirm button
        confirm_rect = Rect(
            rect.x + rect.width - button_width - 16,
            button_y,
            button_width,
            button_height,
        )
        self._confirm_button = UIButton(
            relative_rect=confirm_rect,
            text="CONFIRM",
            manager=manager,
        )
        self._update_confirm_button()

    def _build_footer(self, manager, rect) -> None:
        """Build footer with hints."""
        footer_rect = Rect(rect.x + 8, rect.y + 8, rect.width - 16, 24)
        UILabel(
            relative_rect=footer_rect,
            text="Select category, type, and wrestlers for this match",
            manager=manager,
        )

    def _get_match_type_options(self) -> list[tuple[str, str]]:
        """Get available match type options."""
        return [
            (match_type.name, match_type.id)
            for match_type in self._app.state.match_types.values()
        ]

    def _get_required_wrestler_count(self) -> int:
        """Get the required wrestler count for current category."""
        if self._draft_category is None:
            return 2
        return self._draft_category.size

    def _get_cost_text(self) -> str:
        """Get the cost display text."""
        total_cost = self._calculate_cost()
        return f"Match Cost: ${total_cost:,}"

    def _calculate_cost(self) -> int:
        """Calculate total cost for the match."""
        total = 0

        # Add match type base cost
        if self._draft_match_type_id:
            match_type = self._app.state.match_types.get(self._draft_match_type_id)
            if match_type:
                total += match_type.base_cost

        # Add wrestler booking costs
        for wrestler_id in self._draft_wrestler_ids:
            if wrestler_id and wrestler_id in self._app.state.roster:
                total += self._app.state.wrestler_booking_price(wrestler_id)

        return total

    def _get_rivalry_badges_for_wrestler(self, wrestler_id: str | None) -> list[str]:
        """Return compact rivalry emoji badges for a wrestler."""
        if not wrestler_id:
            return []

        participants = [wid for wid in self._draft_wrestler_ids if wid]
        if len(participants) < 2:
            return []

        badges: list[str] = []
        for wrestler_a_id, wrestler_b_id in combinations(participants, 2):
            if wrestler_id not in (wrestler_a_id, wrestler_b_id):
                continue
            emoji = self._app.state.rivalry_emoji_for_pair(wrestler_a_id, wrestler_b_id)
            if emoji:
                badges.append(emoji)
        return badges

    def _update_confirm_button(self) -> None:
        """Update confirm button enabled state based on validation."""
        required_count = self._get_required_wrestler_count()
        filled_count = sum(1 for wid in self._draft_wrestler_ids if wid)

        if filled_count < required_count:
            self._confirm_button.disable()
            return

        # Check for duplicates
        non_none_ids = [wid for wid in self._draft_wrestler_ids if wid]
        if len(non_none_ids) != len(set(non_none_ids)):
            self._confirm_button.disable()
            return

        self._confirm_button.enable()

    def _on_category_changed(self, category_id: int) -> None:
        """Handle category change - update type options and wrestler slots."""
        # Find the category
        new_category = next(
            (cat for cat in MATCH_CATEGORIES if cat.id == category_id), None
        )
        if new_category is None:
            return

        self._draft_category = new_category

        # Resize wrestler slots
        old_ids = list(self._draft_wrestler_ids)
        self._draft_wrestler_ids = [None] * new_category.size
        for i in range(min(len(old_ids), new_category.size)):
            self._draft_wrestler_ids[i] = old_ids[i]

        # Refresh match type options for the new category
        self._refresh_type_options()

        # Rebuild body to show new slot count
        self._rebuild_body()

    def _refresh_type_options(self) -> None:
        """Refresh match type dropdown options."""
        if self._type_dropdown is None:
            return

        match_type_options = self._get_match_type_options()
        self._type_dropdown.options_list = [opt[0] for opt in match_type_options]
        self._type_dropdown.type_map = {opt[0]: opt[1] for opt in match_type_options}

        # Select first option if current selection is invalid
        current_type_id = self._draft_match_type_id
        valid_ids = {opt[1] for opt in match_type_options}
        if current_type_id not in valid_ids and match_type_options:
            self._draft_match_type_id = match_type_options[0][1]
            self._type_dropdown.selected_option = match_type_options[0][0]

    def _rebuild_body(self) -> None:
        """Rebuild body section with updated wrestler slots.

        Called when category changes to update the number of wrestler slots.
        Clears existing slot panels and recreates them for the new category size.
        """
        manager = getattr(self._app, "ui_manager", None)
        if not manager:
            return

        # Get body zone rect
        zones = self._compute_zones(pygame.display.get_surface().get_rect())
        body_rect = zones["body"]

        # Kill existing slot panels (this also kills their children: buttons and labels)
        for panel in self._slot_panels:
            panel.kill()

        # Clear tracking lists
        self._wrestler_slot_buttons.clear()
        self._rivalry_labels.clear()
        self._slot_panels.clear()

        # Recalculate Y offset (same as _build_body: category + type + cost = 120)
        y_offset = body_rect.y + 128
        slot_height = 70
        slot_spacing = 8

        # Rebuild wrestler slots
        for i in range(self._get_required_wrestler_count()):
            # Slot panel
            slot_rect = Rect(
                body_rect.x + 8,
                y_offset + i * (slot_height + slot_spacing),
                body_rect.width - 16,
                slot_height,
            )
            slot_panel = UIPanel(
                relative_rect=slot_rect,
                manager=manager,
            )

            # Wrestler button
            wrestler_id = (
                self._draft_wrestler_ids[i]
                if i < len(self._draft_wrestler_ids)
                else None
            )
            wrestler = self._app.state.roster.get(wrestler_id) if wrestler_id else None

            button_text = wrestler.name if wrestler else "SELECT WRESTLER"
            button_rect = Rect(8, 10, slot_rect.width - 16, 36)
            button = UIButton(
                relative_rect=button_rect,
                text=button_text,
                manager=manager,
                container=slot_panel,
                object_id=f"wrestler_slot_{i}",
            )
            self._wrestler_slot_buttons.append(button)

            # Rivalry indicator
            rivalries = self._get_rivalry_badges_for_wrestler(wrestler_id)
            rivalry_text = " ".join(rivalries) if rivalries else ""
            rivalry_rect = Rect(8, 48, slot_rect.width - 16, 20)
            rivalry_label = UILabel(
                relative_rect=rivalry_rect,
                text=rivalry_text,
                manager=manager,
                container=slot_panel,
            )
            self._rivalry_labels.append(rivalry_label)
            self._slot_panels.append(slot_panel)

    def _on_wrestler_slot_clicked(self, slot_num: int) -> None:
        """Navigate to wrestler selection screen."""
        # Build exclude list (already selected wrestlers in other slots)
        exclude_ids = [
            wid
            for i, wid in enumerate(self._draft_wrestler_ids)
            if wid and i != slot_num
        ]

        self._router.navigate(
            "wrestler_selection",
            on_select=lambda w: self._on_wrestler_selected(slot_num, w),
            exclude=exclude_ids,
            slot_index=self._slot_index,
        )

    def _on_wrestler_selected(self, slot_num: int, wrestler) -> None:
        """Handle wrestler selection from selection screen."""
        # Validate not duplicate
        for i, wid in enumerate(self._draft_wrestler_ids):
            if i != slot_num and wid == wrestler.id:
                # Duplicate - should not happen due to exclude list
                return

        # Add wrestler to draft
        self._draft_wrestler_ids[slot_num] = wrestler.id

        # Update button text
        button = self._wrestler_slot_buttons[slot_num]
        button.set_text(wrestler.name)

        # Update rivalry indicators
        self._update_rivalry_indicators()

        # Update cost display
        self._cost_label.set_text(self._get_cost_text())

        # Update confirm button state
        self._update_confirm_button()

    def _update_rivalry_indicators(self) -> None:
        """Update rivalry indicator labels for all slots."""
        for i, label in enumerate(self._rivalry_labels):
            wrestler_id = (
                self._draft_wrestler_ids[i]
                if i < len(self._draft_wrestler_ids)
                else None
            )
            rivalries = self._get_rivalry_badges_for_wrestler(wrestler_id)
            label.set_text(" ".join(rivalries) if rivalries else "")

    def _on_confirm_clicked(self) -> None:
        """Save match and return to booking hub."""
        # Validate draft
        required_count = self._get_required_wrestler_count()
        filled_count = sum(1 for wid in self._draft_wrestler_ids if wid)

        if filled_count < required_count:
            return

        # Create match
        wrestlers = [
            self._app.state.roster[wid]
            for wid in self._draft_wrestler_ids
            if wid and wid in self._app.state.roster
        ]

        if self._draft_category is None:
            return

        match = Match(
            wrestlers=wrestlers,
            match_category=self._draft_category,
            match_type_id=self._draft_match_type_id or "",
        )

        # Validate
        errors = self._app.state.validate_match(match, slot_index=self._slot_index)
        if errors:
            # Show error modal
            from ..modals.error import ErrorModal

            error_modal = ErrorModal(
                self._app,
                self._app.ui_manager,
                Rect(0, 0, 480, 800),
                "Validation Error",
                "\n".join(errors),
            )
            error_modal.show()
            return

        # Save to show card
        self._app.state.set_slot(self._slot_index, match)

        # Return to booking hub
        self._router.back()

    def _on_cancel_clicked(self) -> None:
        """Cancel and return to booking hub."""
        self._router.back()

    def _on_clear_slot_clicked(self) -> None:
        """Show confirmation modal and clear slot."""
        from ..modals.confirm import ConfirmModal

        self._confirm_modal = ConfirmModal(
            self._app,
            self._app.ui_manager,
            Rect(0, 0, 480, 800),
            title="Clear Slot?",
            message="Are you sure you want to clear this match slot?",
            on_confirm=self._clear_slot_confirmed,
            on_cancel=None,
            confirm_text="Yes",
            cancel_text="No",
        )
        self._confirm_modal.show()

    def _clear_slot_confirmed(self) -> None:
        """Clear the slot and return to booking hub."""
        self._app.state.clear_slot(self._slot_index)
        self._router.back()

    def handle_event(self, event) -> bool:
        """Handle pygame events for this screen."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # Check wrestler slot buttons
            for i, button in enumerate(self._wrestler_slot_buttons):
                if event.ui_element == button:
                    self._on_wrestler_slot_clicked(i)
                    return True

            # Check action buttons
            if event.ui_element == self._cancel_button:
                self._on_cancel_clicked()
                return True
            elif event.ui_element == self._clear_button:
                self._on_clear_slot_clicked()
                return True
            elif event.ui_element == self._confirm_button:
                self._on_confirm_clicked()
                return True

        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            # Handle category change
            if event.ui_element == self._category_dropdown:
                category_name = event.text
                if hasattr(self._category_dropdown, "category_map"):
                    category_id = self._category_dropdown.category_map.get(
                        category_name, 1
                    )
                    self._on_category_changed(category_id)
                return True

            # Handle type change
            elif event.ui_element == self._type_dropdown:
                type_name = event.text
                if hasattr(self._type_dropdown, "type_map"):
                    self._draft_match_type_id = self._type_dropdown.type_map.get(
                        type_name, ""
                    )
                self._cost_label.set_text(self._get_cost_text())
                return True

        # Pass to confirm modal if active
        if self._confirm_modal:
            return self._confirm_modal.handle_event(event)

        return False

    def update(self, time_delta: float) -> None:
        """Update screen state."""
        if self._confirm_modal:
            self._confirm_modal.update(time_delta)
