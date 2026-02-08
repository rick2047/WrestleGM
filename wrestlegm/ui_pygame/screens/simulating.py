"""Simulating screen with progress indicator."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import pygame_gui
from pygame.rect import Rect
from pygame_gui.core import ObjectID
from pygame_gui.elements import UILabel

from .base import BaseScreen

if TYPE_CHECKING:
    from wrestlegm.ui_pygame.app import WrestleGMApp
    from wrestlegm.ui_pygame.router import Router


class SimulatingScreen(BaseScreen):
    """Show simulation progress and auto-advance to results."""

    # Simulation duration in seconds
    SIMULATION_DURATION = 3.0
    # Progress update interval in seconds
    UPDATE_INTERVAL = 0.05

    def __init__(self, app: "WrestleGMApp", router: "Router") -> None:
        super().__init__(app, router)
        self._progress = 0.0
        self._simulation_complete = False
        self._time_accumulated = 0.0
        self._title_label: Optional[UILabel] = None
        self._progress_label: Optional[UILabel] = None
        self._show_number = app.state.show_index

    def _build_header(self, manager, rect) -> None:
        """Build header with show number."""
        title_rect = Rect(rect.x, rect.y + 10, rect.width, 30)
        self._title_label = UILabel(
            relative_rect=title_rect,
            text=f"SIMULATING SHOW #{self._show_number}",
            manager=manager,
            object_id=ObjectID(class_id="@header_title", object_id="#simulating_title"),
        )

    def _build_body(self, manager, rect) -> None:
        """Build body with progress display."""
        # Center the progress text vertically
        progress_y = rect.y + (rect.height // 2) - 40
        progress_rect = Rect(rect.x, progress_y, rect.width, 40)
        self._progress_label = UILabel(
            relative_rect=progress_rect,
            text="0%",
            manager=manager,
            object_id=ObjectID(
                class_id="@sim_progress", object_id="#simulating_progress"
            ),
        )

    def _build_actions(self, manager, rect) -> None:
        """No actions during simulation."""
        pass

    def _build_footer(self, manager, rect) -> None:
        """Build footer with simulation status."""
        hint_rect = Rect(rect.x + 10, rect.y + 5, rect.width - 20, 20)
        UILabel(
            relative_rect=hint_rect,
            text="Please wait while the show is simulated...",
            manager=manager,
            object_id=ObjectID(class_id="@footer_hint", object_id="#simulating_hint"),
        )

    def update(self, time_delta: float) -> None:
        """Advance progress and run simulation when complete."""
        if self._simulation_complete:
            return

        # Accumulate time
        self._time_accumulated += time_delta

        # Update progress based on time
        if self._time_accumulated >= self.UPDATE_INTERVAL:
            self._time_accumulated = 0.0
            progress_increment = self.UPDATE_INTERVAL / self.SIMULATION_DURATION
            self._progress = min(1.0, self._progress + progress_increment)

            # Update progress label
            if self._progress_label:
                percentage = int(self._progress * 100)
                self._progress_label.set_text(f"{percentage}%")

        # When complete, run simulation and navigate to results
        if self._progress >= 1.0 and not self._simulation_complete:
            self._complete_simulation()

    def _complete_simulation(self) -> None:
        """Run the simulation and navigate to results."""
        self._simulation_complete = True

        # Update label to show completion
        if self._progress_label:
            self._progress_label.set_text("COMPLETE!")

        # Run the actual simulation
        try:
            show = self._app.state.run_show()
            # Navigate to results with the show data
            self._router.navigate("results", show=show)
        except ValueError as e:
            # Handle simulation error via Router
            self._router.show_error(
                title="Simulation Error",
                message=str(e),
            )

    def handle_event(self, event) -> bool:
        """Handle pygame events."""
        return False
