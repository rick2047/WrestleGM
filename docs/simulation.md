# Simulation

## Pipeline
Each match follows a deterministic pipeline implemented in `wrestlegm.sim`:

1. Outcome simulation: compute win probability and sample winner.
2. Rating simulation: calculate match rating in stars.
3. Stat delta simulation: produce popularity and stamina deltas.
4. Show rating aggregation: average match ratings.
5. End-of-show application: apply deltas and clamp stats.

The show pipeline is orchestrated by `GameState.run_show()` which delegates
match simulation to `simulate_show()` and applies the results in
`GameState.apply_show_results()`.

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
- Alignment adds a bonus for Face vs Heel or penalty for Heel vs Heel.
- Match type rating bonus and variance apply.
- One RNG draw applies variance, then ratings clamp to 0-100 and convert to stars.

Formula highlights (from `simulate_rating()`):

- `base_100 = pop_avg * POP_W + sta_avg * STA_W`
- alignment modifier: `+ALIGN_BONUS` (Face vs Heel), `-2*ALIGN_BONUS` (Heel vs Heel)
- `rating_100 = clamp(base_100 + rating_bonus + swing, 0, 100)`
- `rating_stars = round((rating_100 / 100) * 5, 1)`

## Stat Deltas

- Popularity and stamina deltas come directly from match type modifiers.
- Deltas are applied only once after the show completes.

`simulate_stat_deltas()` is responsible for packaging deltas; `GameState` is
responsible for applying them to roster state.

## Show Rating

Show rating is the arithmetic mean of the match ratings. No RNG is used for
aggregation.

`aggregate_show_rating()` returns `0.0` for an empty result list.

## Recovery and Clamping

- Stamina recovery applies only to wrestlers who did not work the show.
- Recovery amount is `STAMINA_RECOVERY_PER_SHOW`.
- Popularity and stamina values clamp to 0-100 after deltas and recovery.

## Deterministic Guarantees

- One RNG instance seeded from game state.
- One RNG draw for outcome and one for rating per match.
- No wall-clock time or UI-driven inputs affect simulation results.
