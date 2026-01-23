"""Simulating screen."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Static

from ..routes import RESULTS


class SimulatingScreen(Screen):
    """Simulating screen that runs the show and auto-advances.

    Responsibilities:
    - Call GameState.run_show() to perform simulation and state updates.
    - Advance to ResultsScreen after a short delay.
    """

    def compose(self) -> ComposeResult:
        """Build the simulating screen layout."""

        yield Static("Simulating show...")
        yield Footer()

    def on_mount(self) -> None:
        """Run the show and schedule auto-advance."""

        self.app.state.run_show()
        self.set_timer(0.4, self.advance)

    def advance(self) -> None:
        """Advance to the results screen."""

        self.app.navigate(RESULTS)
