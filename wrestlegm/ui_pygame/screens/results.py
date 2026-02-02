"""Results screen for displaying show outcomes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import pygame_gui
from pygame.rect import Rect
from pygame_gui.elements import UIButton, UILabel

from wrestlegm.models import Match, MatchResult, PromoResult

from .base import BaseScreen

if TYPE_CHECKING:
    from wrestlegm.models import Show
    from wrestlegm.ui_pygame.app import WrestleGMApp
    from wrestlegm.ui_pygame.router import Router


class ResultsScreen(BaseScreen):
    """Display show results with economy info and match/promo outcomes."""

    def __init__(self, app: "WrestleGMApp", router: "Router", show: "Show") -> None:
        super().__init__(app, router)
        self._show = show
        self._continue_button: Optional[UIButton] = None
        self._results_labels: list[UILabel] = []

    def _build_header(self, manager, rect) -> None:
        """Build header with show results title and money."""
        from wrestlegm.ui.formatting import format_money, format_stars

        # Title - Show Results
        title_rect = Rect(rect.x + 10, rect.y + 5, rect.width // 2, 20)
        UILabel(
            relative_rect=title_rect,
            text=f"SHOW #{self._show.show_index} RESULTS",
            manager=manager,
        )

        # Overall rating
        rating_text = format_stars(self._show.show_rating or 0.0)
        rating_rect = Rect(rect.x + 10, rect.y + 28, rect.width // 2, 20)
        UILabel(
            relative_rect=rating_rect,
            text=f"Rating: {rating_text}",
            manager=manager,
        )

        # Money
        money_rect = Rect(
            rect.x + rect.width // 2, rect.y + 5, rect.width // 2 - 10, 20
        )
        money_text = f"Money: {format_money(self._app.state.money)}"
        UILabel(
            relative_rect=money_rect,
            text=money_text,
            manager=manager,
        )

    def _build_body(self, manager, rect) -> None:
        """Build body with economy summary and per-slot results."""
        from ..constants import MARGIN, PADDING

        y_offset = rect.y + PADDING
        line_height = 22

        # Economy section
        self._add_section_header(
            manager, rect.x + MARGIN, y_offset, rect.width - (MARGIN * 2), "ECONOMY"
        )
        y_offset += line_height

        economy_lines = self._build_economy_lines()
        for line in economy_lines:
            label_rect = Rect(
                rect.x + MARGIN + 10, y_offset, rect.width - (MARGIN * 2) - 20, 18
            )
            UILabel(
                relative_rect=label_rect,
                text=line,
                manager=manager,
            )
            y_offset += 18

        y_offset += PADDING

        # Match/Promo Results section
        self._add_section_header(
            manager,
            rect.x + MARGIN,
            y_offset,
            rect.width - (MARGIN * 2),
            "SLOT RESULTS",
        )
        y_offset += line_height

        # Per-slot results
        for index, (slot, result) in enumerate(
            zip(self._show.scheduled_slots, self._show.results)
        ):
            if y_offset + line_height > rect.y + rect.height:
                break  # Don't overflow

            if isinstance(slot, Match) and isinstance(result, MatchResult):
                self._add_match_result(manager, rect, index, slot, result, y_offset)
            else:
                self._add_promo_result(manager, rect, index, result, y_offset)
            y_offset += line_height + 5

    def _add_section_header(
        self, manager, x: int, y: int, width: int, text: str
    ) -> None:
        """Add a section header label."""
        rect = Rect(x, y, width, 20)
        UILabel(
            relative_rect=rect,
            text=f"--- {text} ---",
            manager=manager,
        )

    def _build_economy_lines(self) -> list[str]:
        """Build economy summary lines."""
        from wrestlegm.ui.formatting import format_money

        lines = []
        if self._show.audience is not None:
            lines.append(f"Audience: {self._show.audience:,}")
        if self._show.gate_income is not None:
            lines.append(f"Gate Income: {format_money(self._show.gate_income)}")
        if self._show.merch_income is not None:
            lines.append(f"Merch Income: {format_money(self._show.merch_income)}")
        if self._show.total_earned is not None:
            lines.append(f"Total Earned: {format_money(self._show.total_earned)}")
        if self._show.show_cost is not None:
            lines.append(f"Show Cost: {format_money(self._show.show_cost)}")
        return lines

    def _add_match_result(
        self,
        manager,
        rect,
        index: int,
        match: Match,
        result: MatchResult,
        y_offset: int,
    ) -> None:
        """Add a match result entry."""
        from wrestlegm.ui.formatting import (
            format_stars,
            slot_label,
            match_category_label,
        )

        label = slot_label(index, "match")
        winner = self._app.state.roster.get(result.winner_id)
        winner_name = winner.name if winner else "Unknown"

        # Count non-winners
        num_losers = len(result.non_winner_ids)

        match_type = self._app.state.match_types.get(result.match_type_id)
        match_type_name = match_type.name if match_type else "Unknown"
        category_name = match_category_label(result.match_category)

        rating_text = format_stars(result.rating)

        # Main line: Match label and result
        main_rect = Rect(rect.x + 10, y_offset, rect.width - 20, 18)
        main_text = f"{label}: {winner_name} def. {num_losers} other(s)"
        UILabel(
            relative_rect=main_rect,
            text=main_text,
            manager=manager,
        )

        # Detail line: Type and rating
        detail_rect = Rect(rect.x + 10, y_offset + 18, rect.width - 20, 18)
        detail_text = f"  {category_name} {match_type_name} {rating_text}"
        UILabel(
            relative_rect=detail_rect,
            text=detail_text,
            manager=manager,
        )

    def _add_promo_result(
        self, manager, rect, index: int, result: PromoResult, y_offset: int
    ) -> None:
        """Add a promo result entry."""
        from wrestlegm.ui.formatting import format_stars, slot_label

        label = slot_label(index, "promo")
        wrestler = self._app.state.roster.get(result.wrestler_id)
        wrestler_name = wrestler.name if wrestler else "Unknown"
        rating_text = format_stars(result.rating)

        promo_rect = Rect(rect.x + 10, y_offset, rect.width - 20, 18)
        promo_text = f"{label}: {wrestler_name} {rating_text}"
        UILabel(
            relative_rect=promo_rect,
            text=promo_text,
            manager=manager,
        )

    def _build_actions(self, manager, rect) -> None:
        """Build actions with Continue button."""
        from ..constants import MARGIN

        button_height = 50
        button_width = 150
        button_y = rect.y + (rect.height - button_height) // 2

        continue_rect = Rect(
            rect.x + (rect.width - button_width) // 2,
            button_y,
            button_width,
            button_height,
        )
        self._continue_button = UIButton(
            relative_rect=continue_rect,
            text="CONTINUE",
            manager=manager,
        )

    def _build_footer(self, manager, rect) -> None:
        """Build footer with continue hint."""
        hint_rect = Rect(rect.x + 10, rect.y + 5, rect.width - 20, 20)
        UILabel(
            relative_rect=hint_rect,
            text="Click Continue to save and return to Game Hub",
            manager=manager,
        )

    def _on_continue(self) -> None:
        """Save game and return to Game Hub."""
        # The show results have already been applied by run_show()
        # Just need to save the game state
        if hasattr(self._app, "session"):
            self._app.session.save_current_slot(self._app.state)

        # Navigate to game hub
        self._router.switch("game_hub")

    def handle_event(self, event) -> bool:
        """Handle pygame events."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self._continue_button:
                self._on_continue()
                return True
        return False

    def update(self, time_delta: float) -> None:
        """Update screen state."""
        pass
