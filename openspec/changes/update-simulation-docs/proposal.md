# Change: Update simulation documentation after engine refactor

## Why
The simulation documentation still describes the old function-based pipeline and outdated class collaboration. After the engine refactor, docs should reflect `SimulationEngine`, `ShowApplier`, and the new ownership of RNG and mutation flow so readers get accurate guidance.

## What Changes
- Update `docs/simulation.md` to describe the engine-based pipeline and state application flow.
- Update `docs/architecture.md` to reflect class collaboration (SimulationEngine, ShowApplier) and new determinism ownership.

## Impact
- Affected specs: `specs/documentation/spec.md`
- Affected code/docs: `docs/simulation.md`, `docs/architecture.md`
