## MODIFIED Requirements
### Requirement: Booking hub behavior
The system SHALL show five slots in fixed order (Match 1, Promo 1, Match 2, Promo 2, Match 3), allow slot selection, show match participant names with alignment emoji, show `Category · Type` for match slots, and enable Run Show only when all slots are booked.

#### Scenario: Run Show enablement
- **WHEN** any slot is empty
- **THEN** Run Show is disabled

#### Scenario: Show category and type for matches
- **WHEN** the booking hub renders a booked match
- **THEN** it shows a `Category · Type` line under the participant list

### Requirement: Match booking flow
The system SHALL edit matches in a dedicated booking screen, require confirmation before committing, and split match category selection (size) from match type selection (rules). The booking screen SHALL open after a category is chosen, render one wrestler row per required slot based on category, filter match types to those allowed for the selected category, allow changing match type via an inline dropdown, default the match type to the first available option when booking an empty slot, mark already-booked wrestlers with a 📅 indicator in the selection list, show popularity and stamina, display alignment via emoji (Face 😃, Heel 😈), render the selection list as a table with Name/Stamina/Popularity columns, include a header row naming the name/stamina/popularity columns, format rows as `{emoji} {name:<18} {sta:>3} {pop:>3}{fatigue}{booked_marker}`, and use 🥱 consistently for low-stamina indicators.

#### Scenario: Category selection before booking
- **WHEN** the user selects a match slot on the booking hub
- **THEN** a match category selection screen is shown
- **AND THEN** choosing a category opens the match booking screen with the required number of wrestler rows

#### Scenario: Default match type on booking
- **WHEN** the user opens match booking for an empty slot
- **THEN** the first available match type for the selected category is pre-selected

#### Scenario: Match type dropdown filtering
- **WHEN** the match booking screen renders for a category
- **THEN** the match type dropdown lists only match types allowed for that category

#### Scenario: Changing match category mid-booking
- **WHEN** the user re-opens category selection for a booked match and chooses a new category
- **THEN** the match keeps the earliest booked wrestlers up to the new category size
- **AND THEN** any excess wrestlers are silently cleared

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

### Requirement: Results presentation
The system SHALL present match and promo results and the overall show rating using star ratings only, and SHALL include `Category · Type` for match results.

#### Scenario: Show results after simulation
- **WHEN** the show completes
- **THEN** results list match winners and non-winners with star ratings, plus the overall show rating
- **AND THEN** match results include a `Category · Type` line under the participants
