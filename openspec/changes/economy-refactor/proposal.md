## Why

Economy logic is currently split across free functions in `wrestlegm/economy.py`, UI screens, and `GameState`, which makes ownership and state flow unclear. We want a single, stateless `EconomySimulator` (plus model-level pricing) so calculations are centralized and deterministic while `GameState` remains the owner of money and show results.

## What Changes

- Introduce a stateless `EconomySimulator` that performs all economy calculations and returns results used by `GameState`.
- Move per-entity pricing logic (e.g., wrestler booking price) onto model helpers so pricing rules live with the entities they price.
- Centralize show-level aggregation rules (unique billing, show cost, min valid show cost) in the simulator instead of scattered call sites.
- Keep economy state (money) owned and persisted by `GameState`, applying deltas from simulator results.
- Refactor UI call sites to use `GameState` economy accessors instead of economy helpers.

## Capabilities

### New Capabilities
- `economy-simulator`: Stateless economy calculation subsystem with model-level pricing helpers.

### Modified Capabilities
- (none)

## Impact

- `wrestlegm/economy.py` refactor into a simulator-based API.
- `wrestlegm/state.py` pipeline updates to delegate economy to the simulator and apply deltas locally.
- `wrestlegm/models.py` gains pricing helpers (e.g., wrestler booking price).
- UI modules updated to use `GameState` accessors for economy data.
- Persistence remains on `GameState` for economy state (money).
