# Change: Add game hub screen

## Why
The main menu currently mixes session-level navigation and gameplay. A dedicated game hub separates meta actions from in-session decisions and provides a stable home screen for future systems.

## What Changes
- Add a Game Hub screen that is the sole gateway to gameplay screens.
- Restrict the Main Menu to New Game and Quit only.
- Route results back to the Game Hub and remove in-session shortcuts to Roster or Main Menu.
- Define hub navigation, including explicit exit to Main Menu without auto-resetting state until New Game.

## UI Mockups

Main Menu
```
┌──────────────────────────────────────┐
│ WrestleGM                            │
│ Main Menu                            │
├──────────────────────────────────────┤
│ ▸ New Game                           │
│                                      │
│   Quit                               │
│                                      │
├──────────────────────────────────────┤
│ ↑↓ Navigate   Enter Select           │
└──────────────────────────────────────┘
```

Game Hub
```
┌──────────────────────────────────────┐
│ WrestleGM                            │
│ Game Hub                             │
├──────────────────────────────────────┤
│ ▸ Book Current Show                  │
│   Episode 12: Rising Tensions        │
│                                      │
│   Roster Overview                    │
│                                      │
│   Exit to Main Menu                  │
├──────────────────────────────────────┤
│ ↑↓ Navigate   Enter Select   Q Quit  │
└──────────────────────────────────────┘
```

## Impact
- Affected specs: ui
- Affected code: wrestlegm/ui.py
