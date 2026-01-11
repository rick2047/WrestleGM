## MODIFIED Requirements
### Requirement: Global navigation keys and footer
The system SHALL use keyboard-only navigation and display a persistent footer that shows key bindings only. Enter SHALL activate the focused widget and Escape SHALL back out of the current screen or modal. Arrow-key focus order SHALL skip disabled action buttons.

#### Scenario: Footer visibility
- **WHEN** any screen is shown
- **THEN** the footer is visible and displays only key bindings

#### Scenario: Arrow-key navigation across actions
- **WHEN** the user presses arrow keys on booking hub, match booking, results, or roster
- **THEN** focus can move from list views to the action buttons and back in a cycle

## ADDED Requirements
### Requirement: Arrow-key navigation consistency
The system SHALL provide cyclical arrow-key navigation across all screens with focusable lists or action buttons.

#### Scenario: Cyclical focus traversal
- **WHEN** the user presses arrow keys on any screen with focusable lists or buttons
- **THEN** focus cycles from the last element back to the first and from the first back to the last
