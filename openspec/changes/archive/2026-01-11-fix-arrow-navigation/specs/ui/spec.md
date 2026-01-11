## MODIFIED Requirements
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
