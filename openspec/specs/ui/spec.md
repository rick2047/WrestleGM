# ui Specification

## Purpose
TBD - created by archiving change add-wrestlegm-mvp. Update Purpose after archive.
## Requirements
### Requirement: Textual MVP screens
The system SHALL provide the MVP screens defined in the PRD using Textual widgets and keyboard-only navigation. The roster screen SHALL read from the session roster stored in `GameState`, render the roster in a table with Name/Stamina/Popularity columns, include a header row naming the name/stamina/popularity columns, format rows as `{emoji} {name:<18} {sta:>3} {pop:>3}{fatigue}`, display alignment via emoji (Face 😃, Heel 😈), truncate names longer than 18 characters to 15 + `...`, and rebuild its list rows on resume without reusing mounted widget IDs.

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

### Requirement: Global navigation keys and footer
The system SHALL use keyboard-only navigation and display a persistent footer that shows key bindings only. Enter SHALL activate the focused widget and Escape SHALL back out of the current screen or modal. Arrow-key focus order SHALL skip disabled action buttons.

#### Scenario: Footer visibility
- **WHEN** any screen is shown
- **THEN** the footer is visible and displays only key bindings

#### Scenario: Arrow-key navigation across actions
- **WHEN** the user presses arrow keys on booking hub, match booking, results, or roster
- **THEN** focus can move from list views to the action buttons and back in a cycle

### Requirement: Booking hub behavior
The system SHALL show three match slots, allow slot selection, and enable Run Show only when all slots are booked.

#### Scenario: Run Show enablement
- **WHEN** any match slot is empty
- **THEN** Run Show is disabled

### Requirement: Match booking flow
The system SHALL edit matches in a dedicated booking screen and require confirmation before committing. The booking screen SHALL default the match type to the first match type entry, mark already-booked wrestlers with a 📅 indicator in the selection list, show popularity and stamina, display alignment via emoji (Face 😃, Heel 😈), render the selection list as a table with Name/Stamina/Popularity columns, include a header row naming the name/stamina/popularity columns, format rows as `{emoji} {name:<18} {sta:>3} {pop:>3}{fatigue}{booked_marker}`, and use 🥱 consistently for low-stamina indicators.

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

### Requirement: Booking validation in UI
The system SHALL block committing invalid matches and running invalid shows according to the booking rules.

#### Scenario: Prevent duplicate wrestler booking
- **WHEN** a wrestler is already booked in another slot
- **THEN** the UI prevents selecting them for a different slot

### Requirement: Results presentation
The system SHALL present match results and the overall show rating using star ratings only.

#### Scenario: Show results after simulation
- **WHEN** the show completes
- **THEN** results list winners, losers, and star ratings, plus the overall show rating

### Requirement: Arrow-key navigation consistency
The system SHALL provide cyclical arrow-key navigation across all screens with focusable lists or action buttons.

#### Scenario: Cyclical focus traversal
- **WHEN** the user presses arrow keys on any screen with focusable lists or buttons
- **THEN** focus cycles from the last element back to the first and from the first back to the last

