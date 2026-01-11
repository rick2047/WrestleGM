## Context
The current UI is implemented in Textual. Migrating to pygame requires a new rendering loop, event handling, and screen management while keeping simulation logic UI-agnostic.

## Goals / Non-Goals
- Goals:
  - Replace Textual UI with a pygame-based interface.
  - Preserve keyboard-only navigation and existing booking flows.
  - Maintain separation between simulation core and UI layer.
- Non-Goals:
  - Rewriting simulation rules or data model.
  - Adding new gameplay features beyond the current MVP.

## Decisions
- Decision: Use a screen/state manager that maps each existing screen to a pygame scene with explicit draw and input hooks.
- Decision: Keep UI state in lightweight view models that adapt `GameState` for rendering.
- Alternatives considered: Retain Textual for menus and embed pygame for matches (rejected for complexity and mixed event loops).

## Risks / Trade-offs
- Risk: pygame rendering loop may require refactoring how input and screen transitions are handled.
  - Mitigation: implement a single dispatcher for input + navigation to mirror current flows.
- Trade-off: Loss of Textual widget conveniences in exchange for richer visuals.

## Migration Plan
1. Stand up pygame application shell with main menu and navigation.
2. Port each screen incrementally, verifying parity with current behaviors.
3. Remove Textual entrypoints and dependencies after pygame parity is reached.

## Open Questions
- Do we need to support mouse input now or later, or keep keyboard-only parity for MVP?
