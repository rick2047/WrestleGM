## Context

WrestleGM currently has no economic system. Booking is costless and results only affect ratings and stats. The simulation is deterministic (seeded RNG), data-driven, and UI-first with Textual. We need to add money, audience, and bankruptcy without breaking determinism or coupling UI and simulation.

## Goals / Non-Goals

**Goals:**
- Introduce promotion-level money with show costs and post-show income.
- Compute audience from card composition (popularity, alignment, rivalries, cooldowns) with deterministic RNG.
- Add gate and merch income derived from audience and show rating.
- Allow debt after a show; enforce bankruptcy when the player tries to book the next show.
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

- **Economy computation flow (order matters for determinism):**
  1. Simulate matches and promos to compute per-slot ratings.
  2. Compute audience inputs (`pop_sum`, `align_score`, `rivalry_count`, `cooldown_count`).
  3. Compute `audience` (includes deterministic RNG swing).
  4. Compute `gate_income` from audience.
  5. Compute `merch_income` from audience and **show rating** (existing `show_rating`, mean of all slot ratings). Merch includes deterministic RNG swing.
  6. Compute `show_cost` and update money: `money = money - show_cost + gate_income + merch_income`.
  7. Defer bankruptcy evaluation until the next show attempt.

- **Formulas / algorithms (initial defaults; tuned later):**
  - **Wrestler booking price (per unique wrestler per show):**
    - `wrestler_price = BASE + A * (pop ** 1.2)`
    - `pop` is popularity (0–100).
    - **Initial defaults:** `BASE = 100`, `A = 10`.
  - **Show cost:**
    - `show_cost = sum(unique_wrestler_price) + sum(match_type.base_cost)`
    - Promos have zero direct cost.
  - **Audience inputs:**
    - `pop_sum`: sum of popularity for all unique booked wrestlers (matches + promos).
    - `align_score`: total count of Face-vs-Heel pairs across all matchups on the card.
      - Singles: `1` if face vs heel, else `0`.
      - Multi-man: count all unordered pairs; increment for each pair with opposite alignment.
    - `rivalry_count`: count of active rivalry pairs featured on the card (unordered pairs across all matches).
    - `cooldown_count`: count of cooldown pairs featured on the card (unordered pairs across all matches).
  - **Audience curve (conceptual):**
    - `audience = base_from_pop(pop_sum) + bonus(align_score, rivalry_count) - penalty(cooldown_count) + rng_swing`
    - Apply curved/nonlinear mappings for bonus/penalty and clamp to `>= 0`.
    - **Initial default:** `base_from_pop(pop_sum) = pop_sum * 20`.
  - **Gate income:**
    - `gate_income = audience * GATE_RATE` (linear; default `GATE_RATE = 1`).
  - **Merch income:**
    - `merch_income = audience * merch_rate(show_rating) + rng_swing`
    - `merch_rate` is a curved mapping of show rating; clamp to `>= 0`.
    - **Initial default:** `merch_rate = clamp(0.05 + 0.02*show_rating + 0.01*show_rating^2, 0.05, 0.25)`.
  - **RNG swing (audience + merch):**
    - Apply a deterministic multiplier in the range `0.8..1.2` (±20%) using the session RNG.
    - Audience and merch use independent draws.

- **Deterministic RNG:**
  - Use the existing session-seeded RNG for audience and merch swings.
  - Keep RNG calls isolated and ordered to avoid unintended changes to match simulation outputs.

- **Bankruptcy rule (explicit):**
  - Allow running a show even if it produces negative money.
  - Bankruptcy is checked when the player attempts to start booking the *next* show (after leaving results).
  - Define `min_valid_show_cost` as the minimum possible cost for any valid 3-match, 2-promo card given the current roster and match types (using the same validation rules as booking).
  - If `current_money < min_valid_show_cost`, the game transitions to **Game Over: Bankruptcy**.
  - No hard debt limit; the only constraint is whether any valid show can be afforded at next show time.

- **UI updates (authoritative mockups embedded for implementation fidelity):**

### Booking Hub

```
┌──────────────────────────────────────────────────────────────┐
│ Money: $1,250     Booking Hub (Show #12)        Cost: $1,480 │
│                 ⚡ x1  🔥 x1  ⚔️ x1   🧊 x1                    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│               Slots (each is a Button)                        │
│                                                              │
│   [ Match 1 · Singles · $450     Riv ⚡ x1 ]                   │
│     😃 Okada vs 😈 Jay White                                   │
│                                                              │
│   [ Promo 1 ]                                                 │
│     😃 Kazuchika Okada                                        │
│                                                              │
│   [ Match 2 · Triple Threat · $520  Riv 🔥 x1  Cool 🧊 x1 ]     │
│     😃 Omega vs 😈 Switchblade vs 😃 Naito                    │
│                                                              │
│   [ Promo 2 ]                                                 │
│     😈 Jay White                                              │
│                                                              │
│   [ Match 3 · Singles · $510     Riv ⚔️ x1 ]                   │
│     😃 Omega vs 😈 Jay White                                   │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│ [ Run Show ]   [ Roster ]   [ Back ]                          │
├──────────────────────────────────────────────────────────────┤
│ ↑/↓ Focus   Enter Select   Esc Back   R Run Show              │
└──────────────────────────────────────────────────────────────┘
```

### Confirm Run Show (Modal)

**Variant A: No debt**

```
┌──────────────────────────────────────────────────────────────┐
│ Money: $1,250                 Confirm Run Show                │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ Run this show now?                                            │
│                                                              │
│ Show Cost: $1,480                                             │
│ After Show (est.): $—                                          │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│ [ Confirm ]                         [ Cancel ]                │
├──────────────────────────────────────────────────────────────┤
│ Enter Confirm   Esc Cancel                                    │
└──────────────────────────────────────────────────────────────┘
```

**Variant B: Will enter debt**

```
┌──────────────────────────────────────────────────────────────┐
│ Money: $900                  Confirm Run Show                 │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ Run this show now?                                            │
│                                                              │
│ Show Cost: $1,480                                             │
│ WARNING: This will put you into debt.                         │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│ [ Confirm ]                         [ Cancel ]                │
├──────────────────────────────────────────────────────────────┤
│ Enter Confirm   Esc Cancel                                    │
└──────────────────────────────────────────────────────────────┘
```

### Show Results

```
┌──────────────────────────────────────────────────────────────┐
│ Money: -$230 (red)        Show Results (Show #12)             │
├──────────────────────────────────────────────────────────────┤
│ Overall Rating: ★★★★☆ (4.0)                                   │
│ Audience: 12,450                                              │
│ Gate Income: $12,450                                          │
│ Merch Income: $3,120                                          │
│ Total Earned: $15,570                                         │
│ Featured: ⚡ x1  🔥 x1  ⚔️ x1   🧊 x1                           │
│                                                              │
│ Results                                                      │
│  • 😃 Okada def. 😈 Jay White       ★★★★☆                     │
│  • Promo: 😃 Okada                  ★★★☆☆                     │
│  • 😃 Omega def. 😈 Jay White ...   ★★★★☆                     │
│  • Promo: 😈 Jay White              ★★★★☆                     │
│  • 😃 Naito def. 😈 Switchblade...  ★★★☆☆                     │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│ [ Continue ]                                                  │
├──────────────────────────────────────────────────────────────┤
│ Enter Continue                                                │
└──────────────────────────────────────────────────────────────┘
```

### Game Over: Bankruptcy

```
┌──────────────────────────────────────────────────────────────┐
│ Money: -$780 (red)          Game Over: Bankruptcy             │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ You cannot run a valid show with your current funds.          │
│                                                              │
│ Final Show: #12                                               │
│ Final Money: -$780                                            │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│ [ Main Menu ]                                                 │
├──────────────────────────────────────────────────────────────┤
│ Enter Main Menu                                               │
└──────────────────────────────────────────────────────────────┘
```

## Risks / Trade-offs

- **Economy tuning may skew difficulty** → Use conservative constants and add tests for bounds; keep constants centralized for tuning.
- **RNG usage could affect determinism** → Isolate RNG calls in a dedicated economy step; add deterministic tests.
- **Bankruptcy rule depends on a "min valid cost" algorithm** → Implement a deterministic lower-bound calculation and document it in code.
- **Audience curve could overshoot or go negative** → Apply clamped curves with a floor and cap.

## Migration Plan

- Update `data/match_types.json` to include `base_cost` for all entries; loader defaults missing values to 0.
- Initialize `GameState.money` when a new game starts (value to be set during tuning).
- No persistence or backfill needed in MVP.

## Open Questions

- Constants for `BASE`, `A`, and the exact curve functions for audience and merch conversion.
- Exact UI label wording for money/cost fields (if any conflicts with layout).
