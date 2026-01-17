## MODIFIED Requirements

### Requirement: Rating simulation formula and bounds
The system SHALL compute match ratings in 0–100 space, apply a list of rating modifiers (with any star-based bonuses converted to 0–100 using 1 star = 20 points), apply variance using one RNG draw, convert to stars, and clamp to 0.0–5.0 stars.

#### Scenario: Rating computation with modifiers
- **WHEN** a match rating is simulated for `N` wrestlers
- **THEN** `base_100 = pop_avg * POP_W + sta_avg * STA_W` using averages across all wrestlers
- **AND THEN** all registered rating modifiers are applied to the `base_100` rating, including a match type bonus modifier
- **AND THEN** one RNG draw applies `swing` in `[-rating_variance, +rating_variance]`
- **AND THEN** `rating_100` is clamped to 0–100 and converted to stars via `round(rating_100 / 20, 1)`
- **AND THEN** the final rating is clamped to 0.0–5.0 stars

### Requirement: Extensible rating modifier system
The system SHALL provide a `RatingModifier` interface that allows for the creation of new rating adjustment logic without modifying the core simulation engine.

#### Scenario: Alignment modifier
- **WHEN** a match is simulated with a `AlignmentModifier`
- **THEN** for 1v1 matches, the modifier returns `+ALIGN_BONUS` for face vs heel, `-2 * ALIGN_BONUS` for heel vs heel, and `0` for face vs face
- **AND THEN** for matches with `N >= 3`, the modifier returns `-2 * ALIGN_BONUS` for all heels, `0` for all faces, `+ALIGN_BONUS` for heels > faces, `0` for heels == faces, and `-ALIGN_BONUS` for faces > heels

#### Scenario: Match type bonus modifier
- **WHEN** a match is simulated with a `MatchTypeBonusModifier`
- **THEN** the modifier returns the match type rating bonus in 0–100 space

#### Scenario: Rivalry modifier
- **WHEN** a match is simulated with a `RivalryModifier`
- **THEN** each active rivalry pair adds a configurable bonus (defined in stars and converted to 0–100 by multiplying by 20)
- **AND THEN** each blowoff pair adds a configurable bonus (defined in stars and converted to 0–100 by multiplying by 20)

#### Scenario: Cooldown modifier
- **WHEN** a match is simulated with a `CooldownModifier`
- **THEN** if any cooldown pair exists in the match, a configurable penalty (defined in stars and converted to 0–100 by multiplying by 20) is applied to the rating

### Requirement: Simulation debug payloads
The system SHALL provide debug payloads for outcome and promo rating simulations that include the intermediate values used to compute results.

#### Scenario: Outcome debug payload
- **WHEN** a match outcome is simulated
- **THEN** the debug payload includes powers, base probabilities, outcome chaos, final probabilities, RNG sample, and winner id

#### Scenario: Promo debug payload
- **WHEN** a promo rating is simulated
- **THEN** the debug payload includes base rating, swing, and rating values
