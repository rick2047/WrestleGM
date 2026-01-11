## MODIFIED Requirements
### Requirement: Textual MVP screens
The system SHALL provide the MVP screens defined in the PRD using Textual widgets and keyboard-only navigation. The roster screen SHALL read from the session roster stored in `GameState`, include a header row naming the name/stamina/popularity columns, format rows as `{emoji} {name:<18} {sta:>3} {pop:>3}{fatigue}`, display alignment via emoji (Face 😃, Heel 😈), truncate names longer than 18 characters to 15 + `...`, and rebuild its list rows on resume without reusing mounted widget IDs.

#### Scenario: Navigate from main menu to booking hub
- **WHEN** the player selects New Game on the main menu
- **THEN** the booking hub screen is shown

#### Scenario: Roster refresh after resume
- **WHEN** the user returns to the roster screen after leaving it
- **THEN** the roster list is rebuilt from the session roster without duplicate widget IDs

#### Scenario: Roster header and row formatting
- **WHEN** the roster screen renders
- **THEN** a header row names the name, stamina, and popularity columns
- **AND THEN** each roster row follows the format `{emoji} {name:<18} {sta:>3} {pop:>3}{fatigue}`
- **AND THEN** wrestler names longer than 18 characters are truncated to 15 + `...`

#### Scenario: Roster alignment emoji mapping
- **WHEN** the roster screen renders
- **THEN** Face alignment uses 😃 and Heel alignment uses 😈

### Requirement: Match booking flow
The system SHALL edit matches in a dedicated booking screen and require confirmation before committing. The booking screen SHALL default the match type to the first match type entry, mark already-booked wrestlers with a 📅 indicator in the selection list, show popularity and stamina, display alignment via emoji (Face 😃, Heel 😈), include a header row naming the name/stamina/popularity columns, format rows as `{emoji} {name:<18} {sta:>3} {pop:>3}{fatigue}{booked_marker}`, and use 🥱 consistently for low-stamina indicators.

#### Scenario: Confirmation modal on booking
- **WHEN** a booking is complete and the user selects Confirm
- **THEN** a modal prompts for final confirmation before saving the slot

#### Scenario: Default match type on booking
- **WHEN** the user opens match booking for an empty slot
- **THEN** the first available match type is pre-selected

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
