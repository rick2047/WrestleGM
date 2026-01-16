## Context
`GameState` currently handles rivalry progression, cooldown tracking, and all persistence orchestration. This mixes simulation state with IO concerns and makes future changes (like evolving rivalry rules or swapping persistence backends) harder to isolate.

## Goals / Non-Goals
- Goals:
  - Encapsulate rivalry state and logic behind a dedicated manager owned by `GameState`.
  - Encapsulate persistence orchestration behind a `SessionManager` that coordinates `GameState` lifecycle and slot metadata.
  - Preserve current gameplay behavior and UI flow.
- Non-Goals:
  - Changing rivalry rules, cooldown timings, or UI behavior.
  - Introducing new save slot behavior or manual save controls.

## Decisions
- Decision: Add `RivalryManager` in `wrestlegm/rivalries.py` and move rivalry/cooldown state plus related methods out of `GameState`.
  - Why: Rivalry state is a cohesive subsystem that benefits from isolated logic and testing.
- Decision: Add `SessionManager` in `wrestlegm/session.py` and move save/load/new-game/slot metadata state out of `GameState`.
  - Why: Persistence orchestration is a separate concern from in-memory game state; this aligns with the persistence spec and makes swapping storage backends easier.

## Alternatives Considered
- Keep everything in `GameState` and only add helper functions.
  - Rejected because it does not clarify ownership or reduce coupling.
- Place `SessionManager` inside `wrestlegm/persistence.py`.
  - Rejected per request to move save logic into a new `session.py` module.

## Risks / Trade-offs
- Risk: UI entry points may need updates to route through `SessionManager` instead of `GameState`.
  - Mitigation: Keep the public method signatures stable or provide thin delegation during transition.
- Risk: Persistence serialization/deserialization must be updated to access rivalry/cooldown state via the manager.
  - Mitigation: Add focused unit tests around save/load and rivalry state round-tripping.

## Migration Plan
1. Introduce `RivalryManager` and move rivalry/cooldown state plus logic from `GameState`.
2. Introduce `SessionManager` and move slot metadata and persistence orchestration out of `GameState`.
3. Update UI entry points and persistence helpers to use the new managers.
4. Update tests for rivalry and persistence to target the new structures.

## Open Questions
- None. `SessionManager` returns `GameState` instances from load/new-game calls, and the UI owns the active state reference.
