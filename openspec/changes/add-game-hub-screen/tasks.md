## 1. Implementation
- [x] 1.1 Add Game Hub screen with Current Show, Roster Overview, and Exit to Main Menu actions.
- [x] 1.2 Update Main Menu to only show New Game and Quit; reinitialize GameState on New Game.
- [x] 1.3 Route Current Show to the booking hub and return Results to the Game Hub.
- [x] 1.4 Remove Results shortcuts to Roster and Main Menu; ensure hub-only navigation.
- [x] 1.5 Update keyboard bindings to reflect hub navigation and Esc behavior.
- [x] 1.6 Add or update tests/manual verification notes for the new navigation flow.

## 2. Manual Verification
- Start app, select New Game, confirm Game Hub appears with show number.
- From Game Hub, open Current Show and return via Back to the hub.
- Run a show, confirm Results only allow Continue back to Game Hub.
- Use Exit to Main Menu and confirm Main Menu shows only New Game and Quit.
