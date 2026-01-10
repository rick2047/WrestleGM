## Context
The simulation logic is implemented as standalone functions with a shared RNG passed through multiple call sites. This makes the flow parameter-heavy and obscures ownership of randomness. A refactor will introduce a `SimulationEngine` class that owns RNG and a `ShowApplier` that handles state mutation and recovery.

## Goals / Non-Goals
- Goals:
  - Centralize RNG ownership in a simulation engine.
  - Keep simulation deterministic and UI-agnostic.
  - Separate state mutation into a `ShowApplier` owned by `GameState`.
  - Improve test structure with class-based grouping.
- Non-Goals:
  - Change simulation formulas or balancing constants.
  - Add persistence or new gameplay systems.

## Decisions
- Introduce `SimulationEngine` in `wrestlegm/sim.py` with methods for outcome, rating, stat deltas, match simulation, and show simulation.
- Remove the standalone simulation function API and update callers to use the engine.
- Add a `ShowApplier` class in `wrestlegm/state.py` to apply deltas, recovery, and clamping.
- Keep `GameState` as the owner of `SimulationEngine` and `ShowApplier` instances, but not RNG.

## Alternatives Considered
- Keep functional API and wrap in a class: rejected to reduce redundancy and enforce a single path.
- Move mutation into the engine: rejected to preserve deterministic simulation outputs and clear separation of concerns.

## Risks / Trade-offs
- Refactor could introduce behavioral regressions if any formula is altered accidentally.
- Removing function API could break external call sites if any exist outside the repo.

## Migration Plan
- Add the engine and applier classes.
- Update `GameState` and tests.
- Remove deprecated function API.
- Run tests to verify determinism and bounds.

## Open Questions
- None.
