# Change: Update simulation documentation after engine refactor

## Why
The simulation documentation still describes the old function-based pipeline and outdated class collaboration. After the engine refactor, docs should reflect `SimulationEngine`, `ShowApplier`, and the new ownership of RNG and mutation flow so readers get accurate guidance.

## What Changes
- Update `docs/simulation.md` to describe the engine-based pipeline and state application flow.
- Update `docs/architecture.md` to reflect class collaboration (SimulationEngine, ShowApplier) and new determinism ownership.
- Update `docs/implementation.md` to reflect SimulationEngine/ShowApplier ownership and current test file locations.
- Update `docs/ui.md` to reflect arrow-key navigation, focus behavior, and disabled-button skipping.
- Add a brief ownership summary callout to `docs/simulation.md`.
- Add a `ShowApplier` node to the architecture class diagram.
- Update `docs/index.md` to reference `uv` for running the app/tests/docs.
- Tidy `docs/api.md` ordering and add a brief intro for generated docs.

## Impact
- Affected specs: `specs/documentation/spec.md`
- Affected code/docs: `docs/simulation.md`, `docs/architecture.md`, `docs/implementation.md`, `docs/ui.md`, `docs/index.md`, `docs/api.md`
