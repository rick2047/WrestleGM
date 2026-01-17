# simulation Specification

## Purpose
TBD - created by archiving change add-wrestlegm-mvp. Update Purpose after archive.
## Requirements
### Requirement: Deterministic match simulation pipeline
The system SHALL simulate each match using an outcome step, rating step, and stat delta step using a single seeded RNG instance owned by a `SimulationEngine`, and SHALL support matches with `N` wrestlers where `N >= 2`.

#### Scenario: Deterministic outcomes with same inputs
- **WHEN** the same roster stats, stipulation config, show card, and seed are used for matches with `N >= 2`
- **THEN** the match winners, ratings, and deltas are identical across runs

### Requirement: RNG governance and hidden inputs
The system SHALL use a single seeded RNG for all simulation randomness and SHALL not depend on wall-clock time, UI state, or other implicit inputs.

#### Scenario: No hidden randomness inputs
- **WHEN** the same explicit inputs and seed are used
- **THEN** outcomes are reproducible without relying on hidden inputs

### Requirement: Outcome simulation formula and RNG discipline
The system SHALL compute winners using the outcome pipeline and use exactly one RNG draw per match for the final probability sample.

#### Scenario: Outcome probability and sampling
- **WHEN** a match is simulated with `N` wrestlers
- **THEN** power is computed per wrestler as `power_i = popularity_i * P_WEIGHT + stamina_i * S_WEIGHT`
- **AND THEN** base probabilities are `p_base_i = power_i / sum(power)`
- **AND THEN** if total power is 0, base probabilities are uniform
- **AND THEN** chaos is applied as `p_final_i = lerp(p_base_i, 1/N, outcome_chaos)`
- **AND THEN** the `p_final_i` values are normalized to sum to 1
- **AND THEN** a single RNG draw `r` selects the winner from the cumulative distribution of `p_final_i`

### Requirement: Rating simulation formula and bounds
The system SHALL compute match ratings in 0–100 space, apply a list of rating modifiers (with any star-based bonuses converted to 0–100 using 1 star = 20 points), apply variance using one RNG draw, convert to stars, and clamp to 0.0–5.0 stars.

#### Scenario: Rating computation with modifiers
- **WHEN** a match rating is simulated for `N` wrestlers
- **THEN** `base_100 = pop_avg * POP_W + sta_avg * STA_W` using averages across all wrestlers
- **AND THEN** all registered rating modifiers are applied to the `base_100` rating
- **AND THEN** `rating_bonus` from the match type is added
- **AND THEN** one RNG draw applies `swing` in `[-rating_variance, +rating_variance]`
- **AND THEN** `rating_100` is clamped to 0–100 and converted to stars via `round(rating_100 / 20, 1)`
- **AND THEN** the final rating is clamped to 0.0–5.0 stars

### Requirement: Stat delta simulation rules
The system SHALL produce popularity and stamina deltas based solely on match type modifiers.

#### Scenario: Winner and loser deltas
- **WHEN** a match completes with `N` wrestlers
- **THEN** the winner receives `popularity_delta_winner` and `-stamina_cost_winner` once
- **AND THEN** each non-winner receives `popularity_delta_loser` and `-stamina_cost_loser` once

#### Scenario: Match rating does not alter deltas
- **WHEN** a match rating is computed
- **THEN** popularity and stamina deltas depend only on match type modifiers

#### Scenario: Stamina costs are fixed by match type
- **WHEN** a match is simulated
- **THEN** stamina deltas use the match type stamina costs without scaling by rating

### Requirement: Show rating aggregation
The system SHALL compute the overall show rating as the arithmetic mean of match and promo ratings.

#### Scenario: Aggregate show rating
- **WHEN** a show has slot ratings for matches and promos
- **THEN** the show rating equals their arithmetic mean

#### Scenario: Empty show rating
- **WHEN** a show has no slot ratings
- **THEN** the show rating is `0.0`

#### Scenario: Show rating uses no RNG
- **WHEN** the show rating is computed
- **THEN** no RNG draws are used

### Requirement: End-of-show state application
The system SHALL apply all stat deltas once per show and clamp popularity and stamina to 0–100.

#### Scenario: Clamp stats after applying deltas
- **WHEN** deltas would push a stat below 0 or above 100
- **THEN** the resulting stat is clamped to the 0–100 range

#### Scenario: Apply deltas once per show
- **WHEN** a show completes
- **THEN** all stat deltas are applied once and order does not change results

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

### Requirement: RNG seed stored in game state
The system SHALL store the simulation RNG seed in game state to support reproducibility during a session.

#### Scenario: Seed retention
- **WHEN** a new game is started with a seed
- **THEN** the seed is retained in state for future simulations in the current session

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

### Requirement: Simulation pipeline stages
The system SHALL run the simulation pipeline in this order: outcome (matches only), rating, stat deltas, show rating aggregation, and end-of-show state application.

#### Scenario: Pipeline order
- **WHEN** a show is simulated and applied
- **THEN** the pipeline stages execute in the defined order

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

### Requirement: Simulation debug payloads
The system SHALL provide debug payloads for outcome, rating, and promo rating simulations that include the intermediate values used to compute results.

#### Scenario: Outcome debug payload
- **WHEN** a match outcome is simulated
- **THEN** the debug payload includes powers, base probabilities, outcome chaos, final probabilities, RNG sample, and winner id

#### Scenario: Rating debug payload
- **WHEN** a match rating is simulated
- **THEN** the debug payload includes averages, alignment modifier, rating bonus, variance, swing, and rating values

#### Scenario: Promo debug payload
- **WHEN** a promo rating is simulated
- **THEN** the debug payload includes base rating, swing, and rating values

### Requirement: Result payloads include deltas and identifiers
The system SHALL include stat deltas in match and promo results, include applied match type modifiers on match results, and record winner/non-winners, rating, match category, and match type identifiers.

#### Scenario: Match result payload
- **WHEN** a match is simulated
- **THEN** the result includes winner id, non-winner ids, rating, match category id, match type id, applied modifiers, and stat deltas

#### Scenario: Promo result payload
- **WHEN** a promo is simulated
- **THEN** the result includes wrestler id, rating, and stat deltas

### Requirement: Simulation test coverage
The system SHALL include tests that cover determinism, outcome normalization, rating bounds, alignment modifiers, multi-man determinism, promo determinism, promo deltas, match deltas, show rating aggregation, and stat clamping.

#### Scenario: Simulation tests run
- **WHEN** simulation tests run
- **THEN** they cover determinism, outcome, rating bounds, alignment, multi-man, promo, deltas, show rating, and clamp behavior

### Requirement: Extensible rating modifier system
The system SHALL provide a `RatingModifier` interface that allows for the creation of new rating adjustment logic without modifying the core simulation engine.

#### Scenario: Alignment modifier
- **WHEN** a match is simulated with a `AlignmentModifier`
- **THEN** for 1v1 matches, the modifier returns `+ALIGN_BONUS` for face vs heel, `-2 * ALIGN_BONUS` for heel vs heel, and `0` for face vs face
- **AND THEN** for matches with `N >= 3`, the modifier returns `-2 * ALIGN_BONUS` for all heels, `0` for all faces, `+ALIGN_BONUS` for heels > faces, `0` for heels == faces, and `-ALIGN_BONUS` for faces > heels

#### Scenario: Rivalry modifier
- **WHEN** a match is simulated with a `RivalryModifier`
- **THEN** each active rivalry pair adds a configurable bonus (defined in stars and converted to 0–100 by multiplying by 20)
- **AND THEN** each blowoff pair adds a configurable bonus (defined in stars and converted to 0–100 by multiplying by 20)

#### Scenario: Cooldown modifier
- **WHEN** a match is simulated with a `CooldownModifier`
- **THEN** if any cooldown pair exists in the match, a configurable penalty (defined in stars and converted to 0–100 by multiplying by 20) is applied to the rating

