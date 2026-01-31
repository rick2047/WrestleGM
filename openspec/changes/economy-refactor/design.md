## Context

Economy calculations are currently split across `wrestlegm/economy.py` functions, `GameState` orchestration, and UI modules that compute booking prices directly. The change introduces a stateless `EconomySimulator` that centralizes calculations while `GameState` remains the owner of money and show-economy outcomes.

## Goals / Non-Goals

**Goals:**
- Introduce a stateless `EconomySimulator` that is invoked in the show simulation pipeline.
- Move per-entity pricing logic (wrestler booking price) onto model helpers.
- Centralize cross-entity aggregation rules (unique billing, show cost, min valid show cost) inside `EconomySimulator`.
- Preserve UI modules unchanged while ensuring new economy access is exposed through `GameState`.
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

- **UI remains unchanged, GameState is the economy interface**: UI modules are not modified. `GameState` will expose economy accessors (e.g., `current_show_cost()`, booking price helpers) that wrap `EconomySimulator`/model helpers. Existing `economy` module functions used by UI will be preserved as thin wrappers to avoid UI edits in this change.
  - Rationale: Keeps UI stable while enabling a single economy access point for new frontends.
  - Alternative considered: Update UI imports to call `GameState` directly. Rejected to meet the “no UI changes” goal.

- **Persistence stays in GameState**: Money and show outputs remain serialized by `GameState`, with no backward-compatibility guarantees for older saves.
  - Rationale: Keeps state management centralized and allows schema changes without migration work.

## Risks / Trade-offs

- **State drift risk** → Mitigation: `compute_show(...)` uses current inputs from `GameState` and returns a full result object; `GameState` applies it immediately.
- **Compatibility layer masks direct UI calls** → Mitigation: mark wrappers as legacy in docstrings and ensure `GameState` accessors are the preferred path for new code.
- **Persistence schema break** → Mitigation: none; save compatibility is explicitly out of scope for this change.

## Migration Plan

1. Introduce `EconomySimulator` with `compute_show(...)` that mirrors existing formulas.
2. Move wrestler booking price logic to `WrestlerState` helper(s); update simulator calculations to use them.
3. Add `EconomySimulator` accessors on `GameState` and route existing economy call sites through the simulator.
4. Preserve economy module wrappers used by UI (no UI edits).
5. Update tests to validate determinism and unchanged outcomes.

## Open Questions

- None. This change assumes no backward-compatibility requirements.
