## Context

WrestleGM currently has no economic system. Booking is costless and results only affect ratings and stats. The simulation is deterministic (seeded RNG), data-driven, and UI-first with Textual. We need to add money, audience, and bankruptcy without breaking determinism or coupling UI and simulation.

## Goals / Non-Goals

**Goals:**
- Introduce promotion-level money with show costs and post-show income.
- Compute audience from card composition (popularity, alignment, rivalries, cooldowns) with deterministic RNG.
- Add gate and merch income derived from audience and show quality.
- Allow debt after a show; enforce bankruptcy if the next valid show cannot be afforded.
- Surface money/audience and debt warnings in booking, confirmation, results, and game over UI.

**Non-Goals:**
- Dynamic pricing, loans, sponsors, or difficulty scaling.
- Multi-promotion economics or persistence/migrations.
- Audience segmentation or detailed merch breakdowns.

## Decisions

- **Data model updates:**
  - Add `GameState.money: int` (can go negative post-show).
  - Add `MatchType.base_cost: int` in `data/match_types.json` and loader (default 0 if missing).
  - Do not store a wrestler booking cost; compute from popularity at runtime.

- **Economy computation flow:**
  - Pre-show cost: `sum(unique_wrestler_price) + sum(match_type.base_cost)`; promos cost 0.
  - Wrestler price: `BASE + A * (pop ^ 1.2)` using popularity only; charged once per unique wrestler per show.
  - Post-show income: compute audience after simulation, then gate income from audience and merch income from audience × show quality conversion. Apply income after results are computed.

- **Audience model:**
  - Inputs: `pop_sum` (unique booked wrestlers, including promos), `align_score`, `rivalry_count`, `cooldown_count`, plus a small deterministic RNG swing.
  - Apply curved mapping for rivalry/alignment bonuses and cooldown penalties; enforce a non-negative floor.
  - Promos influence audience only through wrestler popularity (no promo-quality effect).

- **Deterministic RNG:**
  - Use the existing session-seeded RNG for audience and merch swings to preserve determinism.
  - Keep RNG calls isolated and ordered to avoid unintended changes to match simulation outputs.

- **Bankruptcy rule:**
  - Allow running a show even if it produces negative money.
  - At next show attempt, if no valid show can be afforded, transition to a terminal “Game Over: Bankruptcy” screen.

- **UI updates:**
  - Booking hub shows per-slot match cost, total show cost, and current money (red if negative).
  - Run-show confirmation modal always appears; display debt warning when cost exceeds current money.
  - Results screen shows audience, gate income, merch income, total earned, and current money.

## Risks / Trade-offs

- **Economy tuning may skew difficulty** → Use conservative constants and add tests for bounds; keep constants centralized for tuning.
- **RNG usage could affect determinism** → Isolate RNG calls in a dedicated economy step; add deterministic tests.
- **Bankruptcy rule ambiguity (what is a “valid” show?)** → Define and test “valid” as existing card validation with minimum possible cost.
- **Audience curve could overshoot or go negative** → Apply clamped curves with a floor and cap.

## Migration Plan

- Update `data/match_types.json` to include `base_cost` for all entries; loader defaults missing values to 0.
- Initialize `GameState.money` when a new game starts (value to be set during tuning).
- No persistence or backfill needed in MVP.

## Open Questions

- Constants for `BASE` and `A`, and the exact curve functions for audience and merch conversion.
- Multi-man rivalry/cooldown counting (all pairs vs. primary pairs).
- Whether merch RNG should be independent of audience RNG.
- Definition of “minimum cost” for bankruptcy checks (cheapest valid card vs. any valid card).
