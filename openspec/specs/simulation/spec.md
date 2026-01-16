# simulation Specification

## Purpose
TBD - created by archiving change add-wrestlegm-mvp. Update Purpose after archive.
## Requirements
### Requirement: Deterministic match simulation pipeline
The system SHALL simulate each match using an outcome step, rating step, and stat delta step using a single seeded RNG instance owned by a `SimulationEngine`, and SHALL support matches with `N` wrestlers where `N >= 2`.

#### Scenario: Deterministic outcomes with same inputs
- **WHEN** the same roster stats, stipulation config, show card, and seed are used for matches with `N >= 2`
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
The system SHALL compute match ratings in 0–100 space with alignment and match type modifiers, apply variance using one RNG draw, convert to stars, apply rivalry bonuses and blowoff multipliers in star space, apply a cooldown penalty if any cooldown pair exists, and clamp to 0.0–5.0 stars.

#### Scenario: Rating computation with rivalry and cooldown
- **WHEN** a match rating is simulated for `N` wrestlers
- **THEN** `base_100 = pop_avg * POP_W + sta_avg * STA_W` using averages across all wrestlers
- **AND THEN** alignment modifiers apply based on face/heel counts (all heels: `-2 * ALIGN_BONUS`, all faces: `0`, heels > faces: `+ALIGN_BONUS`, heels == faces: `0`, faces > heels: `-ALIGN_BONUS`)
- **AND THEN** `rating_bonus` is added
- **AND THEN** one RNG draw applies `swing` in `[-rating_variance, +rating_variance]`
- **AND THEN** `rating_100` is clamped to 0–100 and converted to stars via `round((rating_100/100)*5, 1)`
- **AND THEN** each active rivalry pair adds `+0.25` stars
- **AND THEN** each blowoff pair adds `+0.5` stars
- **AND THEN** if any cooldown pair exists in the match, `-1.0` stars is applied once
- **AND THEN** the final rating is clamped to 0.0–5.0 stars

### Requirement: Stat delta simulation rules
The system SHALL produce popularity and stamina deltas based solely on match type modifiers.

#### Scenario: Winner and loser deltas
- **WHEN** a match completes with `N` wrestlers
- **THEN** the winner receives `popularity_delta_winner` and `-stamina_cost_winner` once
- **AND THEN** each non-winner receives `popularity_delta_loser` and `-stamina_cost_loser` once

### Requirement: Show rating aggregation
The system SHALL compute the overall show rating as the arithmetic mean of match and promo ratings.

#### Scenario: Aggregate show rating
- **WHEN** a show has slot ratings for matches and promos
- **THEN** the show rating equals their arithmetic mean

#### Scenario: Empty show rating
- **WHEN** a show has no slot ratings
- **THEN** the show rating is `0.0`

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

### Requirement: Simulation engine ownership
The system SHALL centralize RNG ownership and simulation methods in a `SimulationEngine` class and remove the standalone functional simulation API.

#### Scenario: Simulation runs through engine
- **WHEN** a show is simulated
- **THEN** the `SimulationEngine` is used to compute outcomes, ratings, and deltas

### Requirement: Deterministic promo simulation pipeline
The system SHALL simulate each promo using a rating step and a stat delta step using the same seeded RNG instance owned by a `SimulationEngine`.

#### Scenario: Deterministic promo ratings with same inputs
- **WHEN** the same wrestler stats and seed are used
- **THEN** promo ratings and deltas are identical across runs

### Requirement: Show simulation order
The system SHALL simulate show slots in card order and return results in the same order.

#### Scenario: Preserve card order in results
- **WHEN** a show card is simulated
- **THEN** the results list follows the original slot order

### Requirement: Promo rating simulation formula and bounds
The system SHALL compute promo ratings in 0–100 space from mic skill and popularity, apply variance using one RNG draw with `PROMO_VARIANCE = 8`, clamp, and convert to 0.0–5.0 stars using the shared conversion rules.

#### Scenario: Promo rating computation and clamping
- **WHEN** a promo rating is simulated
- **THEN** `base_100 = mic_skill * 0.7 + popularity * 0.3`
- **AND THEN** one RNG draw applies `swing` in `[-PROMO_VARIANCE, +PROMO_VARIANCE]`
- **AND THEN** `rating_100` is clamped to 0–100 and converted to stars via `round((rating_100/100)*5, 1)`

### Requirement: Promo stat delta rules
The system SHALL apply fixed popularity deltas based on promo quality and grant stamina recovery during promos.

#### Scenario: Promo popularity deltas
- **WHEN** a promo rating is below 50
- **THEN** the wrestler popularity delta is -5
- **AND WHEN** a promo rating is at least 50
- **THEN** the wrestler popularity delta is +5

#### Scenario: Promo stamina recovery
- **WHEN** a wrestler appears in a promo slot
- **THEN** the wrestler stamina delta is `floor(STAMINA_RECOVERY_PER_SHOW / 2)`
