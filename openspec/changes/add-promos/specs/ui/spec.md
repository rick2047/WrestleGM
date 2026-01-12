## ADDED Requirements
### Requirement: Promo booking flow
The system SHALL provide a promo booking screen that edits a single wrestler for a promo slot and requires confirmation before committing.

#### Scenario: Empty promo slot booking
- **WHEN** the user opens promo booking for an empty slot
- **THEN** the screen shows a single Wrestler field and a disabled Confirm action

#### Scenario: Confirm promo booking
- **WHEN** the user selects Confirm with a valid wrestler selected
- **THEN** a confirmation modal prompts for final confirmation before saving the slot

### Requirement: Shared wrestler selection for promos
The system SHALL reuse the existing wrestler selection screen for promo booking and may change only the contextual title text.

#### Scenario: Promo wrestler selection layout
- **WHEN** the user opens wrestler selection from promo booking
- **THEN** the table layout, columns, and indicators match the match-booking selection screen

## MODIFIED Requirements
### Requirement: Booking hub behavior
The system SHALL show five slots in fixed order (Match 1, Promo 1, Match 2, Promo 2, Match 3), allow slot selection, and enable Run Show only when all slots are booked.

#### Scenario: Run Show enablement
- **WHEN** any slot is empty
- **THEN** Run Show is disabled

### Requirement: Booking validation in UI
The system SHALL block committing invalid matches and running invalid shows according to the booking rules.

#### Scenario: Prevent duplicate wrestler booking
- **WHEN** a wrestler is already booked in another slot
- **THEN** the UI prevents selecting them for a different slot

#### Scenario: Allow low-stamina promos
- **WHEN** a wrestler has stamina below `STAMINA_MIN_BOOKABLE`
- **THEN** the UI still allows selecting them for a promo slot

### Requirement: Results presentation
The system SHALL present match and promo results and the overall show rating using star ratings only.

#### Scenario: Show results after simulation
- **WHEN** the show completes
- **THEN** results list match winners/losers and promo performers with star ratings, plus the overall show rating
