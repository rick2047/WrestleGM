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
- Decision: Make `GameState` the owner of persistence orchestration (save/load/new game).
  - Why: Keeps lifecycle control centralized and avoids UI-driven I/O.
- Decision: Keep simulation and show application pure with no I/O.
  - Why: Preserves deterministic behavior and testability.

## Ownership and Integration Points
- Persistence module: `wrestlegm/persistence.py` (new) owns file I/O and JSON serialization for save slots, and is invoked by `GameState`.
- Game state ownership: `GameState` exposes save/load/new-game operations and stores the active slot.
- UI ownership: UI screens route user intent to `GameState` operations and handle navigation only.
- No persistence in simulation: `GameState.run_show` and `ShowApplier` remain pure with no I/O.

## Risks / Trade-offs
- Risk: Tight coupling between GameState structure and save format.
  - Mitigation: Explicit version field and centralized serialization.

## Migration Plan
- MVP only supports version 1 and blocks higher versions.

## Open Questions
- None.
