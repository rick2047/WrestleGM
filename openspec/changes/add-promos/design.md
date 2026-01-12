## Context
The MVP show loop currently supports three match slots and match-only simulation. Issue 21 requires promo booking and simulation while preserving the deterministic, data-driven architecture.

## Goals / Non-Goals
- Goals:
  - Add promo slots to the show card and results.
  - Reuse existing wrestler selection UI for promo booking.
  - Define deterministic promo rating and progression rules.
  - Keep simulation/UI separation intact.
- Non-Goals:
  - Promo types, storylines, or chaining mechanics.
  - Any data persistence changes beyond adding `mic_skill`.

## Decisions
- Decision: Promo slots use a single wrestler and the shared wrestler selection screen.
  - Why: Keeps UI minimal and consistent with the PRD.
- Decision: Promo quality uses a weighted mic/pop formula with fixed global variance.
  - Proposed: `base_100 = mic * 0.7 + pop * 0.3`, variance range `PROMO_VARIANCE = 8` in 0–100 space.
- Decision: Promo popularity deltas are fixed based on quality threshold.
  - Proposed: quality < 50 → -5, quality ≥ 50 → +5.
- Decision: Promo stamina recovery is half of the between-show recovery amount.
  - Proposed: `promo_recovery = floor(STAMINA_RECOVERY_PER_SHOW / 2)`.
- Decision: Show rating averages all slot stars (matches + promos).

## Risks / Trade-offs
- Promo variance range and fixed deltas may require tuning; start with a conservative variance to avoid large swings.
- Allowing low-stamina wrestlers in promos reduces stamina gating complexity but must be clearly scoped to promo booking only.

## Migration Plan
- Add `mic_skill` to `data/wrestlers.json` and default values for existing entries.
- Update simulation engine and show applier to include promo slots.
- Update UI booking hub and results screens to render promo slots.

## Open Questions
- None (resolved via issue 21 inputs).
