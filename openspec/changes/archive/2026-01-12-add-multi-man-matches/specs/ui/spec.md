## MODIFIED Requirements
### Requirement: Match booking flow
The system SHALL edit matches in a dedicated booking screen and require confirmation before committing. The booking screen SHALL select a match type before wrestler selection, render one wrestler row per required slot (2–4), allow re-selecting match type from the booking screen, default the match type to the first entry when booking an empty slot, mark already-booked wrestlers with a 📅 indicator in the selection list, show popularity and stamina, display alignment via emoji (Face 😃, Heel 😈), render the selection list as a table with Name/Stamina/Popularity columns, include a header row naming the name/stamina/popularity columns, format rows as `{emoji} {name:<18} {sta:>3} {pop:>3}{fatigue}{booked_marker}`, and use 🥱 consistently for low-stamina indicators.

#### Scenario: Default match type on booking
- **WHEN** the user opens match booking for an empty slot
- **THEN** the first available match type is pre-selected
- **AND THEN** the match booking screen renders the required number of wrestler rows for that match type

#### Scenario: Match type selection before booking
- **WHEN** the user selects a match slot on the booking hub
- **THEN** a match type selection screen is shown
- **AND THEN** choosing a match type opens the match booking screen

#### Scenario: Changing match type mid-booking
- **WHEN** the user changes match type from the match booking screen
- **THEN** the match keeps the earliest booked wrestlers up to the new match size
- **AND THEN** any excess wrestlers are silently cleared
- **AND THEN** the booking screen renders the new required number of wrestler rows

#### Scenario: Booked wrestler indicator
- **WHEN** the user opens the wrestler selection list
- **THEN** already-booked wrestlers include a 📅 indicator in their row
- **AND THEN** wrestlers selected in the current booking draft also show the 📅 indicator

#### Scenario: Wrestler stats and alignment in selection list
- **WHEN** the user opens the wrestler selection list
- **THEN** each wrestler row shows popularity, stamina, and an alignment emoji
- **AND THEN** Face alignment uses 😃 and Heel alignment uses 😈

#### Scenario: Selection row formatting
- **WHEN** the wrestler selection list renders
- **THEN** each row follows the format `{emoji} {name:<18} {sta:>3} {pop:>3}{fatigue}{booked_marker}`
- **AND THEN** wrestler names longer than 18 characters are truncated to 15 + `...`

#### Scenario: Selection header row
- **WHEN** the wrestler selection list renders
- **THEN** a header row names the name, stamina, and popularity columns

#### Scenario: Low-stamina indicator consistency
- **WHEN** the UI renders a low-stamina indicator
- **THEN** it uses the 🥱 emoji everywhere

### Requirement: Booking hub behavior
The system SHALL show five slots in fixed order (Match 1, Promo 1, Match 2, Promo 2, Match 3), allow slot selection, and enable Run Show only when all slots are booked.

#### Scenario: Run Show enablement
- **WHEN** any slot is empty
- **THEN** Run Show is disabled

### Requirement: Results presentation
The system SHALL present match and promo results and the overall show rating using star ratings only.

#### Scenario: Show results after simulation
- **WHEN** the show completes
- **THEN** results list match winners and non-winners with star ratings, plus the overall show rating

## ADDED Requirements
### Requirement: Match type selection screen
The system SHALL provide a match type selection screen when booking a match slot and use the selected match type to determine the required wrestler count in match booking.

#### Scenario: Match type selection
- **WHEN** the user selects a match slot on the booking hub
- **THEN** the match type selection screen lists Singles, Triple Threat, and Fatal 4-Way
- **AND THEN** selecting a match type opens match booking for that slot
