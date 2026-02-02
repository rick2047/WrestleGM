"""Entry point for WrestleGM MVP.

Full Game Loop Test:
    1. Launch app -> Main Menu (New Game, Load Game, Quit)
    2. New Game -> Save Slot Selection -> Pick empty slot -> Create game -> Game Hub
    3. Game Hub -> Booking -> Booking Hub (show card with 5 slots: 3 matches + 2 promos)
    4. Booking Hub -> Click slot -> Match Booking (select category, type, wrestlers)
    5. Match Booking -> Wrestler Selection -> Pick wrestlers -> Return
    6. Confirm booking -> Return to Booking Hub
    7. Fill remaining slots -> Click Simulate -> Simulating Screen (progress bar)
    8. Simulating -> Results Screen (match outcomes, ratings, economy)
    9. Results -> Continue -> Save game -> Return to Game Hub
    10. Repeat from step 3

Edge Cases Handled:
    - Bankruptcy: Triggers when money < 0, shows Bankruptcy Screen with restart options
    - Corrupt saves: Error modal displayed, returns to Main Menu
    - Duplicate wrestlers: Validation prevents booking same wrestler twice in one show
    - Low stamina wrestlers: Filtered from selection list
    - Debt warning: Confirmation modal shown before booking if show will cause debt
    - Validation errors: Error modal with specific message

Save/Load Compatibility:
    - Saves are compatible between Textual and pygame versions
    - Both use the same SessionManager and save format
    - Saves contain: GameState (roster, history, economy), show slot assignments
    - Textual UI available in wrestlegm/ui/ for backward compatibility

Backward Compatibility Notes:
    - Textual UI code remains in wrestlegm/ui/ unchanged
    - Use --ui textual flag to launch Textual UI
    - Game logic (state.py, sim.py, economy.py) is UI-agnostic
    - All existing tests pass without modification
"""

import argparse


def main() -> None:
    """Run the WrestleGMApp with UI selection via CLI args."""
    parser = argparse.ArgumentParser(
        description="WrestleGM - Wrestling promotion management game"
    )
    parser.add_argument(
        "--ui",
        choices=["pygame", "textual"],
        default="pygame",
        help="UI to use: pygame (default, touch-friendly) or textual (terminal)",
    )
    args = parser.parse_args()

    if args.ui == "textual":
        # Textual UI (terminal-based)
        from wrestlegm.ui import WrestleGMApp as TextualWrestleGMApp

        app = TextualWrestleGMApp()
        app.run()
    else:
        # Pygame UI (default, touch-friendly mobile interface)
        from wrestlegm.ui_pygame import WrestleGMApp

        app = WrestleGMApp()
        app.run()


if __name__ == "__main__":
    main()
