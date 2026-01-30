## ADDED Requirements

### Requirement: Economy simulation stage
The system SHALL compute audience, gate income, and merch income after match/promo ratings are computed and before money is updated.

#### Scenario: Economy simulation ordering
- **WHEN** a show completes ratings
- **THEN** audience is computed from card composition and rivalry state
- **AND THEN** gate income is computed from audience
- **AND THEN** merch income is computed from audience and show rating

### Requirement: Audience input computation
The system SHALL compute audience inputs from the booked card and rivalry state using deterministic logic.

#### Scenario: Audience inputs are deterministic
- **WHEN** the same card, rivalry state, and RNG seed are used
- **THEN** `pop_sum`, `align_score`, `rivalry_count`, and `cooldown_count` are identical

### Requirement: RNG usage for economy
The system SHALL use the session-seeded RNG for audience and merch swings and use independent draws for each.

#### Scenario: Deterministic economy RNG
- **WHEN** a show is simulated with the same seed and inputs
- **THEN** the audience and merch RNG multipliers are identical across runs
