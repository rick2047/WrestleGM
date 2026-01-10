## 1. Simulation Engine
- [ ] 1.1 Introduce `SimulationEngine` with RNG ownership and match/show simulation methods.
- [ ] 1.2 Remove standalone simulation function API and update call sites.

## 2. State Mutation
- [ ] 2.1 Add `ShowApplier` in `wrestlegm/state.py` to apply deltas, recovery, and clamping.
- [ ] 2.2 Update `GameState` to use `SimulationEngine` and `ShowApplier` without owning RNG.

## 3. Tests
- [ ] 3.1 Migrate simulation tests into a new engine-focused test module.
- [ ] 3.2 Group tests by class and expand coverage for engine determinism and bounds.

## 4. Validation
- [ ] 4.1 Run `uv run pytest`.
