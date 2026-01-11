## Context
The current UI uses Textual, but the target experience is a pygame-based graphical application. The simulation core should remain UI-agnostic.

## Goals / Non-Goals
- Goals:
  - Use pygame for rendering and input handling.
  - Preserve existing gameplay flows and screen content.
  - Keep the simulation core independent of the UI framework.
- Non-Goals:
  - Redesign gameplay systems or simulation rules.
  - Add new gameplay features beyond the existing MVP screens.

## Decisions
- Decision: Introduce pygame as the UI framework.
  - Why: It provides the desired graphical runtime and input handling.
- Decision: Implement a scene-based UI structure that mirrors the existing Textual screens.
  - Why: It minimizes behavioral changes while swapping the UI technology.

## Risks / Trade-offs
- Risk: pygame introduces a new dependency and runtime requirements.
  - Mitigation: Keep the dependency scope limited to the UI layer.

## Migration Plan
1. Add pygame application bootstrap and main loop.
2. Replace Textual screens with pygame scenes in parity with the existing flow.
3. Remove Textual entrypoints once pygame UI is functional.

## Open Questions
- Should mouse input be supported alongside keyboard controls for the MVP?
