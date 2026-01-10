# Change: Refactor Simulation Into Engine Class

## Why
The simulation flow is currently spread across many functions with parameter-heavy signatures. Introducing a `SimulationEngine` class will centralize RNG ownership, improve cohesion, and clarify responsibilities while keeping mutation inside game state.

## What Changes
- Introduce a `SimulationEngine` class that owns the RNG and exposes match/show simulation methods.
- Remove the standalone simulation function API in favor of the engine class.
- Add a `ShowApplier` class to encapsulate state mutation and recovery logic.
- Migrate simulation tests into a new engine-focused test module with class-based grouping.

## Impact
- Affected specs: `specs/simulation/spec.md`, `specs/game-loop/spec.md`
- Affected code/docs: `wrestlegm/sim.py`, `wrestlegm/state.py`, `tests/`
