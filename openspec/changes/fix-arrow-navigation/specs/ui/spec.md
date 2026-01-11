## MODIFIED Requirements
### Requirement: Global navigation keys and footer
The system SHALL use keyboard-only navigation and display a persistent footer that shows key bindings only. Arrow keys SHALL move focus between list views and action buttons on booking hub, match booking, and results screens.

#### Scenario: Footer visibility
- **WHEN** any screen is shown
- **THEN** the footer is visible and displays only key bindings

#### Scenario: Arrow-key navigation across actions
- **WHEN** the user presses arrow keys on booking hub, match booking, or results
- **THEN** focus can move from list views to the action buttons and back
