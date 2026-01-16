# Change: Add save/load persistence with autosave and slot selection

## Why
Players lose all progress when the app exits, which undermines long-term progression. Save/load persistence allows resuming a promotion across sessions.

## What Changes
- Add a persistence layer that saves full game state to fixed slot files in `dist/data/save`.
- Introduce save slots (3 for MVP, future-safe up to 5) with immutable names.
- Autosave on Results screen Continue after show apply/recovery.
- Add Load Game to the Main Menu with shared Save Slot Selection flow.
- Add Save Slot Selection screen plus Name Slot and Overwrite Slot modals.
- Load resumes at a clean show boundary and opens Booking Hub.
- Save file versioning (v1 only) blocks unsupported versions.
- Add tests for save/load integrity, RNG determinism, and UI flows.

## Non-Goals
- Mid-show saving or manual save actions.
- Save slot deletion, renaming, or branching timelines.
- Cloud sync or cross-device persistence.
- Save schema migration tooling in MVP.

## UI Mockups

Main Menu
```
▸ New Game
  Load Game
  Quit
```

Save Slot Selection
```
┌──────────────────────────────────────┐
│ WrestleGM                            │
│ Load Game                            │
├──────────────────────────────────────┤
│ ▸ Slot 1 · My Promotion · Show #12   │
│                                      │
│   Slot 2 · [ Empty ]                 │
│                                      │
│   Slot 3 · Indie Run · Show #4       │
│                                      │
├──────────────────────────────────────┤
│ ↑↓ Navigate   Enter Select  Esc Back │
└──────────────────────────────────────┘
```

Name Save Slot
```
            ┌──────────────────────────┐
            │ Name Save Slot            │
            ├──────────────────────────┤
            │ [ My Promotion        ]  │
            │                          │
            │ [ Confirm ]  [ Cancel ] │
            └──────────────────────────┘
```

Overwrite Save Slot
```
            ┌──────────────────────────┐
            │ Overwrite Slot 1?        │
            ├──────────────────────────┤
            │ This will replace        │
            │ "My Promotion".          │
            │                          │
            │ [ Confirm ]  [ Cancel ] │
            └──────────────────────────┘
```

## Impact
- Affected specs: `ui`, `persistence`
- Affected code: `wrestlegm/ui.py`, `wrestlegm/state.py`, new persistence module (TBD)
- Data storage: add `dist/` to `.gitignore` and write saves under `dist/data/save/`
