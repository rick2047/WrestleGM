## ADDED Requirements
### Requirement: Deterministic match simulation pipeline
The system SHALL simulate each match using an outcome step, rating step, and stat delta step using a single seeded RNG instance.

#### Scenario: Deterministic outcomes with same inputs
- **WHEN** the same roster stats, match type config, show card, and seed are used
- **THEN** the match winners, ratings, and deltas are identical across runs

### Requirement: Outcome simulation formula and RNG discipline
The system SHALL compute winners using the outcome pipeline and use exactly one RNG draw per match for the final probability sample.

#### Scenario: Outcome probability and sampling
- **WHEN** a match is simulated
- **THEN** power is computed as `popularity * P_WEIGHT + stamina * S_WEIGHT`
- **AND THEN** `diff = power_A - power_B`
- **AND THEN** `p_base = clamp(0.5 + diff / D_SCALE, P_MIN, P_MAX)`
- **AND THEN** `p_final = lerp(p_base, 0.5, outcome_chaos)`
- **AND THEN** a single RNG draw `r` determines the winner (`r < p_final` means A wins)

### Requirement: Rating simulation formula and bounds
The system SHALL compute match ratings in 0–100 space with alignment and match type modifiers, apply variance using one RNG draw, clamp, and convert to 0.0–5.0 stars.

#### Scenario: Rating computation and clamping
- **WHEN** a match rating is simulated
- **THEN** `base_100 = pop_avg * POP_W + sta_avg * STA_W`
- **AND THEN** alignment modifiers apply (Face vs Heel: `+ALIGN_BONUS`, Heel vs Heel: `-2*ALIGN_BONUS`, Face vs Face: `0`)
- **AND THEN** `rating_bonus` is added
- **AND THEN** one RNG draw applies `swing` in `[-rating_variance, +rating_variance]`
- **AND THEN** `rating_100` is clamped to 0–100 and converted to stars via `round((rating_100/100)*5, 1)`

### Requirement: Stat delta simulation rules
The system SHALL produce popularity and stamina deltas based solely on match type modifiers.

#### Scenario: Winner and loser deltas
- **WHEN** a match completes
- **THEN** winner deltas use `popularity_delta_winner` and `-stamina_cost_winner`
- **AND THEN** loser deltas use `popularity_delta_loser` and `-stamina_cost_loser`

### Requirement: Show rating aggregation
The system SHALL compute the overall show rating as the arithmetic mean of match ratings.

#### Scenario: Aggregate show rating
- **WHEN** a show has three match ratings
- **THEN** the show rating equals their arithmetic mean

### Requirement: End-of-show state application
The system SHALL apply all stat deltas once per show and clamp popularity and stamina to 0–100.

#### Scenario: Clamp stats after applying deltas
- **WHEN** deltas would push a stat below 0 or above 100
- **THEN** the resulting stat is clamped to the 0–100 range

### Requirement: Between-show stamina recovery
The system SHALL restore stamina only for wrestlers who did not appear on the previous show and clamp results to 0–100.

#### Scenario: Resting wrestler recovery
- **WHEN** a wrestler did not participate in the last show
- **THEN** their stamina increases by `STAMINA_RECOVERY_PER_SHOW` and is clamped to 0–100
