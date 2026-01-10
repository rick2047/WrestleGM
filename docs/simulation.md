# Simulation

## Pipeline
Each match follows a deterministic pipeline implemented in `wrestlegm.sim`:

1. Outcome simulation: compute win probability and sample winner.
2. Rating simulation: calculate match rating in stars.
3. Stat delta simulation: produce popularity and stamina deltas.
4. Show rating aggregation: average match ratings.
5. End-of-show application: apply deltas and clamp stats.

## Outcome Simulation

- Power is computed from popularity and stamina weights.
- Base win probability is derived from power difference and clamped.
- Match type chaos pulls the probability toward 50/50.
- One RNG draw decides the winner.

## Rating Simulation

- Base rating uses weighted popularity and stamina averages.
- Alignment adds a bonus for Face vs Heel or penalty for Heel vs Heel.
- Match type rating bonus and variance apply.
- One RNG draw applies variance, then ratings clamp to 0-100 and convert to stars.

## Stat Deltas

- Popularity and stamina deltas come directly from match type modifiers.
- Deltas are applied only once after the show completes.

## Show Rating

Show rating is the arithmetic mean of the match ratings. No RNG is used for
aggregation.

## Deterministic Guarantees

- One RNG instance seeded from game state.
- One RNG draw for outcome and one for rating per match.
- No wall-clock time or UI-driven inputs affect simulation results.
