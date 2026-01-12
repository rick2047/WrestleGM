## MODIFIED Requirements
### Requirement: Deterministic match simulation pipeline
The system SHALL simulate each match using an outcome step, rating step, and stat delta step using a single seeded RNG instance owned by a `SimulationEngine`, and SHALL support matches with 2–4 wrestlers.

#### Scenario: Deterministic outcomes with same inputs
- **WHEN** the same roster stats, match type config, show card, and seed are used for matches with 2–4 wrestlers
- **THEN** the match winners, ratings, and deltas are identical across runs

### Requirement: Outcome simulation formula and RNG discipline
The system SHALL compute winners using the outcome pipeline and use exactly one RNG draw per match for the final probability sample.

#### Scenario: Outcome probability and sampling
- **WHEN** a match is simulated with `N` wrestlers
- **THEN** power is computed per wrestler as `power_i = popularity_i * P_WEIGHT + stamina_i * S_WEIGHT`
- **AND THEN** base probabilities are `p_base_i = power_i / sum(power)`
- **AND THEN** chaos is applied as `p_final_i = lerp(p_base_i, 1/N, outcome_chaos)`
- **AND THEN** the `p_final_i` values are normalized to sum to 1
- **AND THEN** a single RNG draw `r` selects the winner from the cumulative distribution of `p_final_i`

### Requirement: Rating simulation formula and bounds
The system SHALL compute match ratings in 0–100 space with alignment and match type modifiers, apply variance using one RNG draw, clamp, and convert to 0.0–5.0 stars.

#### Scenario: Rating computation and clamping
- **WHEN** a match rating is simulated for `N` wrestlers
- **THEN** `base_100 = pop_avg * POP_W + sta_avg * STA_W` using averages across all wrestlers
- **AND THEN** alignment modifiers apply based on face/heel counts (all heels: `-2 * ALIGN_BONUS`, all faces: `0`, heels > faces: `+ALIGN_BONUS`, heels == faces: `0`, faces > heels: `-2 * ALIGN_BONUS`)
- **AND THEN** `rating_bonus` is added
- **AND THEN** one RNG draw applies `swing` in `[-rating_variance, +rating_variance]`
- **AND THEN** `rating_100` is clamped to 0–100 and converted to stars via `round((rating_100/100)*5, 1)`

### Requirement: Stat delta simulation rules
The system SHALL produce popularity and stamina deltas based solely on match type modifiers.

#### Scenario: Winner and loser deltas
- **WHEN** a match completes with `N` wrestlers
- **THEN** the winner receives `popularity_delta_winner` and `-stamina_cost_winner` once
- **AND THEN** each non-winner receives `popularity_delta_loser` and `-stamina_cost_loser` once
