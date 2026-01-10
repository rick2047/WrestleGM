# ui Specification

## Purpose
TBD - created by archiving change add-wrestlegm-mvp. Update Purpose after archive.
## Requirements
### Requirement: Textual MVP screens
The system SHALL provide the MVP screens defined in the PRD using Textual widgets and keyboard-only navigation.

#### Scenario: Navigate from main menu to booking hub
- **WHEN** the player selects New Game on the main menu
- **THEN** the booking hub screen is shown

### Requirement: Global navigation keys and footer
The system SHALL use keyboard-only navigation and display a persistent footer that shows key bindings only.

#### Scenario: Footer visibility
- **WHEN** any screen is shown
- **THEN** the footer is visible and displays only key bindings

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

