# Simulation

## Pipeline
Each match follows a deterministic pipeline owned by `SimulationEngine` in
`wrestlegm.sim`:

1. Outcome simulation: compute win probability and sample winner.
2. Rating simulation: calculate match rating in stars.
3. Stat delta simulation: produce popularity and stamina deltas.
4. Show rating aggregation: average match ratings.
5. End-of-show application: apply deltas, recovery, and clamp stats.

The show pipeline is orchestrated by `GameState.run_show()` which delegates
match simulation to `SimulationEngine.simulate_show()` and applies results via
`ShowApplier`.

`SimulationEngine` owns the RNG and is the only place randomness is used.

## Ownership Summary

- `SimulationEngine`: owns RNG and produces match results.
- `ShowApplier`: applies deltas, recovery, and clamping.
- `GameState`: orchestrates the show lifecycle and stores results.

## Outcome Simulation

- Power is computed from popularity and stamina weights.
- Base win probability is derived from power difference and clamped.
- Match type chaos pulls the probability toward 50/50.
- One RNG draw decides the winner.

Formula highlights (from `simulate_outcome()`):

- `power = popularity * P_WEIGHT + stamina * S_WEIGHT`
- `p_base = clamp(0.5 + diff / D_SCALE, P_MIN, P_MAX)`
- `p_final = lerp(p_base, 0.5, outcome_chaos)`

Constants live in `wrestlegm/constants.py`.

## Rating Simulation

- Base rating uses weighted popularity and stamina averages.
- Rating modifiers apply in 0-100 space (alignment, rivalry bonuses, cooldown penalties).
- Rivalry and cooldown values are defined in stars and converted using 1 star = 20 points.
- Match type rating bonus and variance apply after modifiers.
- One RNG draw applies variance, then ratings clamp to 0-100 and convert to stars.

Formula highlights (from `simulate_rating()`):

- `base_100 = pop_avg * POP_W + sta_avg * STA_W`
- alignment modifier: `+ALIGN_BONUS` (Face vs Heel), `-2*ALIGN_BONUS` (Heel vs Heel)
- `rating_100 = clamp(base_100 + modifiers + rating_bonus + swing, 0, 100)`
- `rating_stars = round(rating_100 / 20, 1)`

## Stat Deltas

- Popularity and stamina deltas come directly from match type modifiers.
- Deltas are applied only once after the show completes.

`SimulationEngine.simulate_stat_deltas()` packages deltas; `ShowApplier` applies
them to roster state.

## Show Rating

Show rating is the arithmetic mean of the match ratings. No RNG is used for
aggregation.

`aggregate_show_rating()` returns `0.0` for an empty result list.

## Recovery and Clamping

- Stamina recovery applies only to wrestlers who did not work the show.
- Recovery amount is `STAMINA_RECOVERY_PER_SHOW`.
- Popularity and stamina values clamp to 0-100 after deltas and recovery.

## Deterministic Guarantees

- `SimulationEngine` owns a single RNG seeded from game state.
- One RNG draw for outcome and one for rating per match.
- No wall-clock time or UI-driven inputs affect simulation results.
