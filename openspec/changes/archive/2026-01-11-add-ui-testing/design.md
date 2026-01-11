## Context
The project uses Textual for UI and pytest for testing. Issue #18 requests UI testing using Textual's test utilities, including flow tests and SVG snapshots for key screens.

## Goals / Non-Goals
- Goals:
  - Use Textual test utilities to drive deterministic, keyboard-only UI flows.
  - Capture SVG snapshots for canonical, stable screen states.
  - Keep snapshot baselines in-repo and enforce a fixed registry.
- Non-Goals:
  - No runtime screenshot capture during gameplay.
  - No pixel-perfect terminal screenshots beyond SVG output.
  - No gameplay or simulation changes.

## Decisions
- Decision: Split UI tests into flow tests and snapshot tests.
  - Why: Flow tests validate navigation and state; snapshots validate layout stability.
- Decision: Store baselines under `tests/snapshots/` and enforce a fixed registry.
  - Why: Keeps snapshot scope bounded and reviewable.
- Decision: Gate snapshot tests behind flow tests in CI.
  - Why: Reduce snapshot noise when behavior is already failing.

## Risks / Trade-offs
- Risk: Snapshot noise from unstable states.
  - Mitigation: Only snapshot canonical screens and stable end states.
- Risk: Snapshot sprawl.
  - Mitigation: Enforce a closed registry and fail on missing or extra snapshots.

## Migration Plan
1. Add flow tests for core UI journeys.
2. Add snapshot tests and baseline SVGs.
3. Update CI workflow order and artifacts.

## Open Questions
- None.
