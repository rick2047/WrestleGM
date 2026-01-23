"""Show results screen."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Footer, Static

from wrestlegm.models import Match

from ..formatting import build_name_cell, format_stars, match_category_label, slot_label


class ResultsScreen(Screen):
    """Show results screen for completed matches.

    Responsibilities:
    - Render per-match winners and star ratings.
    - Display the overall show rating.
    - Route to the game hub.
    """

    BINDINGS = [
        ("enter", "continue", "Continue"),
        ("left", "focus_prev", "Prev"),
        ("right", "focus_next", "Next"),
        ("up", "focus_prev", "Prev"),
        ("down", "focus_next", "Next"),
    ]

    def compose(self) -> ComposeResult:
        """Build the results screen layout."""

        yield Static("Show Results", classes="section-title")
        self.results = Static("")
        yield self.results
        self.show_rating = Static("")
        yield self.show_rating
        self.continue_button = Button("Continue", id="continue")
        yield self.continue_button
        yield Footer()

    def on_mount(self) -> None:
        """Populate results when the screen is shown."""

        self.refresh_view()
        self.continue_button.focus()

    def refresh_view(self) -> None:
        """Update match results and show rating text."""

        show = self.app.state.last_show
        if show is None:
            self.results.update("No results.")
            self.show_rating.update("")
            return
        lines = []
        for index, (slot, result) in enumerate(
            zip(show.scheduled_slots, show.results), start=0
        ):
            if isinstance(slot, Match):
                label = slot_label(index, "match")
                winner = self.app.state.roster[result.winner_id]
                non_winners = ", ".join(
                    build_name_cell(
                        self.app.state.roster[wrestler_id].name,
                        self.app.state.roster[wrestler_id].alignment,
                    )
                    for wrestler_id in result.non_winner_ids
                )
                match_type = self.app.state.match_types.get(result.match_type_id)
                match_type_name = match_type.name if match_type else "Unknown"
                category_name = match_category_label(result.match_category_id)
                lines.append(label)
                lines.append(f" {build_name_cell(winner.name, winner.alignment)} def. {non_winners}")
                lines.append(f" {category_name} · {match_type_name}")
                lines.append(f" {format_stars(result.rating)}")
                lines.append("")
            else:
                label = slot_label(index, "promo")
                wrestler = self.app.state.roster[result.wrestler_id].name
                lines.append(label)
                lines.append(f" {wrestler}")
                lines.append(f" {format_stars(result.rating)}")
                lines.append("")
        self.results.update("\n".join(lines).strip())
        rating = show.show_rating or 0.0
        self.show_rating.update(f"Show Rating: {format_stars(rating)}")

    def action_continue(self) -> None:
        """Return to the game hub."""
        # Fail fast if the save state is invalid; inputs are validated upstream.
        self.app.session.save_current_slot(self.app.state)
        self.app.show_game_hub()

    def action_focus_next(self) -> None:
        """Move focus to the next results action."""

        self._move_focus(1)

    def action_focus_prev(self) -> None:
        """Move focus to the previous results action."""

        self._move_focus(-1)

    def _move_focus(self, delta: int) -> None:
        """Cycle focus across results action buttons."""

        focus_order = [self.continue_button]
        focused = self.app.focused
        if focused not in focus_order:
            focus_order[0].focus()
            return
        index = focus_order.index(focused)
        focus_order[(index + delta) % len(focus_order)].focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle Continue button presses."""

        if event.button.id == "continue":
            self.action_continue()
