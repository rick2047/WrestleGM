## Context

Economy calculations are currently split across `wrestlegm/economy.py` functions, `GameState` orchestration, and UI modules that compute booking prices directly. The change introduces a stateless `EconomySimulator` that centralizes calculations while `GameState` remains the owner of money and show-economy outcomes.

## Goals / Non-Goals

**Goals:**
- Introduce a stateless `EconomySimulator` that is invoked in the show simulation pipeline.
- Move per-entity pricing logic (wrestler booking price) onto model helpers.
- Centralize cross-entity aggregation rules (unique billing, show cost, min valid show cost) inside `EconomySimulator`.
- Refactor UI modules to use `GameState` economy accessors instead of calling economy helpers directly.
- Keep persistence on `GameState` (money remains `GameState` state).

**Non-Goals:**
- Change economy formulas, RNG ranges, or pricing curves.
- Change UI layout, widgets, or behaviors.
- Alter booking validation rules or simulation outcomes.

## Decisions

- **Stateless EconomySimulator**: `EconomySimulator.compute_show(...)` takes inputs and returns an immutable result (show_cost, audience, gate_income, merch_income, total_earned). `GameState` applies deltas to its own money and stores show outputs.
  - Rationale: Centralizes calculation while keeping ownership of economy state in `GameState`.
  - Alternative considered: A stateful manager owning money. Rejected to keep state localized to `GameState` and simplify persistence.

- **Model-level pricing helpers**: Introduce `WrestlerState.booking_price()` (and/or `WrestlerState.booking_price_for(popularity)`) in `wrestlegm/models.py`. `EconomySimulator` consumes these helpers when computing show costs.
  - Rationale: Pricing rules live with the priced entity; changes to booking price no longer require touching economy logic.
  - Alternative considered: A separate `pricing.py` module. Deferred to keep scope small and avoid new modules unless needed.

- **Aggregation belongs to EconomySimulator**: Unique billing across a show card, total show cost, and minimum valid show cost calculations live in `EconomySimulator` (not in UI or free functions).
  - Rationale: These computations combine multiple entities and are part of the economy domain.

- **UI uses GameState accessors**: UI modules will be updated to call `GameState` accessors (e.g., `current_show_cost()`, `wrestler_booking_price(...)`) instead of economy helpers.
  - Rationale: Ensures a single UI integration surface for future frontends.
  - Alternative considered: Preserve economy helpers for UI. Rejected to enforce the single access point requirement.

- **Persistence stays in GameState**: Money and show outputs remain serialized by `GameState`, with no backward-compatibility guarantees for older saves.
  - Rationale: Keeps state management centralized and allows schema changes without migration work.

## Risks / Trade-offs

- **State drift risk** → Mitigation: `compute_show(...)` uses current inputs from `GameState` and returns a full result object; `GameState` applies it immediately.
- **Persistence schema break** → Mitigation: none; save compatibility is explicitly out of scope for this change.

## Migration Plan

1. Introduce `EconomySimulator` with `compute_show(...)` that mirrors existing formulas.
2. Move wrestler booking price logic to `WrestlerState` helper(s); update simulator calculations to use them.
3. Add `EconomySimulator` accessors on `GameState` and route existing economy call sites through the simulator.
4. Refactor UI economy usage to go through `GameState` accessors.
5. Update tests to validate determinism and unchanged outcomes.

## Open Questions

- None. This change assumes no backward-compatibility requirements.
