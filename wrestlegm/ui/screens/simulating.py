"""Simulating screen."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import Static

from ..formatting import format_money
from ..routes import RESULTS
from .standard import StandardScreen


class SimulatingScreen(StandardScreen):
    """Simulating screen that runs the show and auto-advances.

    Responsibilities:
    - Call GameState.run_show() to perform simulation and state updates.
    - Advance to ResultsScreen after a short delay.
    """

    TITLE = "Simulating"

    def header_right(self) -> str:
        return f"Money: {format_money(self.app.state.money)}"

    def compose_body(self) -> ComposeResult:
        """Build the simulating screen layout."""

        yield Static("Simulating show...")

    def on_mount(self) -> None:
        """Run the show and schedule auto-advance."""

        super().on_mount()
        self.app.state.run_show()
        self.update_header()
        self.set_timer(0.4, self.advance)

    def advance(self) -> None:
        """Advance to the results screen."""

        self.app.navigate(RESULTS)
