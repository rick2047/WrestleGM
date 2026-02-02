"""Main pygame application for WrestleGM."""

from __future__ import annotations

import pygame
import pygame_gui

from wrestlegm.data import load_wrestlers, load_match_types
from wrestlegm.session import SessionManager
from wrestlegm.state import GameState


class WrestleGMApp:
    """Main pygame application."""

    def __init__(self) -> None:
        # Initialize pygame
        pygame.init()

        # Create window at 480x800 or scalable
        self._screen = pygame.display.set_mode((480, 800), pygame.RESIZABLE)
        pygame.display.set_caption("WrestleGM")

        # Initialize pygame_gui UIManager
        self._ui_manager = pygame_gui.UIManager((480, 800))

        # Load game data and create GameState
        wrestlers = load_wrestlers()
        match_types = load_match_types()
        self._state = GameState(wrestlers, match_types)

        # Initialize SessionManager for save/load
        self._session = SessionManager(wrestlers, match_types)

        # Create Router
        from .router import Router

        self._router = Router(self)

        # Create and register TransitionManager
        from .transitions import TransitionManager

        self._transition_manager = TransitionManager()
        self._router.set_transition_manager(self._transition_manager)

        # Register screens (will be added as they're implemented)
        self._register_screens()

        # Set up automatic screen rebuilding after navigation
        self._router.set_on_navigate_callback(self._rebuild_current_screen)

        # Clock for frame rate
        self._clock = pygame.time.Clock()
        self._running = False

    def _register_screens(self) -> None:
        """Register all screen routes.

        Screens will be registered here as they are implemented.
        """
        from .screens import (
            BankruptcyScreen,
            BookingHubScreen,
            GameHubScreen,
            MainMenuScreen,
            MatchBookingScreen,
            PromoBookingScreen,
            ResultsScreen,
            RosterScreen,
            SaveSlotSelectionScreen,
            SimulatingScreen,
            WrestlerSelectionScreen,
        )

        self._router.register("main_menu", MainMenuScreen)
        self._router.register("save_slots", SaveSlotSelectionScreen)
        self._router.register("game_hub", GameHubScreen)
        self._router.register("booking_hub", BookingHubScreen)
        self._router.register("match_booking", MatchBookingScreen)
        self._router.register("promo_booking", PromoBookingScreen)
        self._router.register("wrestler_selection", WrestlerSelectionScreen)
        self._router.register("simulating", SimulatingScreen)
        self._router.register("results", ResultsScreen)
        self._router.register("roster", RosterScreen)
        self._router.register("bankruptcy", BankruptcyScreen)

    @property
    def session(self):
        """Access to session manager for save/load."""
        return self._session

    @property
    def state(self) -> GameState:
        """Access to game state for screens."""
        return self._state

    @property
    def ui_manager(self) -> pygame_gui.UIManager:
        """Access to pygame_gui UIManager."""
        return self._ui_manager

    @property
    def router(self):
        """Access to router for navigation."""
        return self._router

    @property
    def transition_manager(self):
        """Access to transition manager."""
        return self._transition_manager

    def quit(self) -> None:
        """Quit the application."""
        self._running = False

    def _rebuild_current_screen(self) -> None:
        """Rebuild the current screen's UI elements.

        Clears the UI manager and calls build() on the current screen.
        This is called automatically after navigation to ensure UI elements exist.
        """
        # Clear all existing UI elements
        self._ui_manager.clear_and_reset()

        # Get current screen and build it
        current = self._router.current
        if current:
            from pygame import Rect

            from .constants import DESIGN_HEIGHT, DESIGN_WIDTH

            current.build(self._ui_manager, Rect(0, 0, DESIGN_WIDTH, DESIGN_HEIGHT))

    def run(self) -> None:
        """Main game loop with transition support."""
        self._running = True

        # Navigate to main menu (rebuild happens automatically via callback)
        self._router.navigate("main_menu")

        while self._running:
            time_delta = self._clock.tick(60) / 1000.0

            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False

                self._ui_manager.process_events(event)

                # Pass to current screen (skip during active transition)
                if not self._transition_manager.is_active():
                    current = self._router.current
                    if current:
                        current.handle_event(event)

            # Update
            self._ui_manager.update(time_delta)

            # Update transition if active
            if self._transition_manager.is_active():
                transition_complete = self._transition_manager.update(time_delta)
                if transition_complete:
                    self._router.complete_transition()
                    self._rebuild_current_screen()
            else:
                current = self._router.current
                if current:
                    current.update(time_delta)

            # Render
            self._screen.fill((26, 26, 26))  # Background #1a1a1a
            self._ui_manager.draw_ui(self._screen)

            # Render transition overlay if active
            if self._transition_manager.is_active():
                self._transition_manager.render(self._screen)

            pygame.display.flip()

        pygame.quit()
