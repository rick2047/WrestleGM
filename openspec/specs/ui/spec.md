# ui Specification

## Purpose
TBD - created by archiving change add-wrestlegm-mvp. Update Purpose after archive.
## Requirements
### Requirement: Textual MVP screens
The system SHALL provide the MVP screens defined in the PRD using Textual widgets and keyboard-only navigation. The roster screen SHALL read from the session roster stored in `GameState` and rebuild its list rows on resume without reusing mounted widget IDs.

#### Scenario: Navigate from main menu to booking hub
- **WHEN** the player selects New Game on the main menu
- **THEN** the booking hub screen is shown

#### Scenario: Roster refresh after resume
- **WHEN** the user returns to the roster screen after leaving it
- **THEN** the roster list is rebuilt from the session roster without duplicate widget IDs

### Requirement: Global navigation keys and footer
The system SHALL use keyboard-only navigation and display a persistent footer that shows key bindings only. Arrow keys SHALL move focus between list views and action buttons on booking hub, match booking, results, and confirmation modal screens. Enter SHALL activate the focused widget and Escape SHALL back out of the current screen or modal. Arrow-key focus order SHALL skip disabled action buttons.

#### Scenario: Footer visibility
- **WHEN** any screen is shown
- **THEN** the footer is visible and displays only key bindings

#### Scenario: Arrow-key navigation across actions
- **WHEN** the user presses arrow keys on booking hub, match booking, or results
- **THEN** focus can move from list views to the action buttons and back

#### Scenario: Booking hub focus order
- **WHEN** the user navigates with arrow keys on the booking hub
- **THEN** focus moves from the match slot list to Run Show to Back and back to match slot 1
- **AND THEN** disabled Run Show is skipped when navigating

#### Scenario: Match booking focus order
- **WHEN** the user navigates with arrow keys on match booking
- **THEN** focus moves from the match fields to Confirm, Clear Slot, and Cancel
- **AND THEN** disabled Clear Slot is skipped when navigating

#### Scenario: Confirmation modal navigation
- **WHEN** the user opens the confirmation modal
- **THEN** arrow keys move focus between Confirm and Cancel and Enter activates the focused action

### Requirement: Booking hub behavior
The system SHALL show three match slots, allow slot selection, and enable Run Show only when all slots are booked.

#### Scenario: Run Show enablement
- **WHEN** any match slot is empty
- **THEN** Run Show is disabled

### Requirement: Match booking flow
The system SHALL edit matches in a dedicated booking screen and require confirmation before committing.

#### Scenario: Confirmation modal on booking
- **WHEN** a booking is complete and the user selects Confirm
- **THEN** a modal prompts for final confirmation before saving the slot

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

