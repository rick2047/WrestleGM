## Context
The current game session is in-memory only. We need a persistence layer that serializes full game state without touching simulation logic or UI-only concerns.

## Goals / Non-Goals
- Goals:
  - Persist and restore a full game state at show boundaries.
  - Keep RNG determinism by restoring the exact seed.
  - Keep persistence above simulation and show application layers.
- Non-Goals:
  - Mid-show saving, manual saves, save deletion, or migration tooling.

## Decisions
- Decision: Store saves as JSON files under `dist/data/save` with fixed filenames per slot.
  - Why: Human-readable, fixture-friendly, minimal dependencies.
- Decision: Keep persistence orchestration in UI flow after Results Continue.
  - Why: Aligns with existing flow and avoids ShowApplier performing I/O.
- Decision: Add a dedicated persistence module for serialization/deserialization.
  - Why: Keeps `state` and `ui` focused and maintains separation of concerns.

## Ownership and Integration Points
- Persistence module: `wrestlegm/persistence.py` (new) owns file I/O and JSON serialization for save slots.
- App-level ownership: `WrestleGMApp` stores the active slot id and a persistence service instance.
- Load flow entry: `MainMenuScreen.on_list_view_selected` routes to `SaveSlotSelectionScreen` (new) and calls the persistence module to load into `GameState` when a slot is chosen.
- New game flow entry: `WrestleGMApp.new_game` is invoked after `NameSaveSlotModal` confirmation to create a fresh `GameState` and assign the current slot.
- Autosave trigger: `ResultsScreen.action_continue` calls the persistence module to save the active slot before `switch_screen(...)`.
- No persistence in simulation: `GameState.run_show` and `ShowApplier` remain pure with no I/O.

## Risks / Trade-offs
- Risk: Tight coupling between GameState structure and save format.
  - Mitigation: Explicit version field and centralized serialization.

## Migration Plan
- MVP only supports version 1 and blocks higher versions.

## Open Questions
- None.
