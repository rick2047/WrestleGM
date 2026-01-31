## 1. Simulator Core

- [x] 1.1 Add model-level pricing helper(s) (e.g., `WrestlerState.booking_price`) and update economy calculations to use them
- [x] 1.2 Implement `EconomySimulator` with stateless `compute_show(...)` returning show economy results
- [x] 1.3 Move show-level aggregation logic (unique billing, show cost, min valid show cost) into `EconomySimulator`

## 2. GameState Integration

- [x] 2.1 Wire `GameState.run_show()` to call `EconomySimulator.compute_show(...)` and apply money/show outputs locally
- [x] 2.2 Update `GameState.current_show_cost()` / `min_valid_show_cost()` / `is_bankrupt()` to use the simulator
- [x] 2.3 Add `GameState` economy accessors needed by UI (without changing UI modules)

## 3. Economy Module Surface

- [x] 3.1 Refactor `wrestlegm/economy.py` to expose simulator-based wrappers used by existing call sites
- [x] 3.2 Remove or inline obsolete economy helper functions that are no longer used after refactor

## 4. Tests

- [x] 4.1 Update economy tests to target `EconomySimulator` and model pricing helpers
- [x] 4.2 Add regression coverage to ensure show economy outputs remain deterministic and unchanged
- [x] 4.3 Add pricing helper tests (booking price from popularity/state/definition)
