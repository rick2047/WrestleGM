## MODIFIED Requirements
### Requirement: Rating simulation formula and bounds
The system SHALL compute match ratings in 0–100 space with alignment and match type modifiers, apply variance using one RNG draw, convert to stars, apply rivalry bonuses and blowoff multipliers in star space, apply a cooldown penalty if any cooldown pair exists, and clamp to 0.0–5.0 stars.

#### Scenario: Rating computation with rivalry and cooldown
- **WHEN** a match rating is simulated for `N` wrestlers
- **THEN** `base_100 = pop_avg * POP_W + sta_avg * STA_W` using averages across all wrestlers
- **AND THEN** alignment modifiers apply based on face/heel counts (all heels: `-2 * ALIGN_BONUS`, all faces: `0`, heels > faces: `+ALIGN_BONUS`, heels == faces: `0`, faces > heels: `-2 * ALIGN_BONUS`)
- **AND THEN** `rating_bonus` is added
- **AND THEN** one RNG draw applies `swing` in `[-rating_variance, +rating_variance]`
- **AND THEN** `rating_100` is clamped to 0–100 and converted to stars via `round((rating_100/100)*5, 1)`
- **AND THEN** each active rivalry pair adds `+0.25` stars
- **AND THEN** each blowoff pair adds `+0.5` stars
- **AND THEN** if any cooldown pair exists in the match, `-1.0` stars is applied once
- **AND THEN** the final rating is clamped to 0.0–5.0 stars
