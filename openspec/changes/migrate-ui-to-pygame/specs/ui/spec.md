## RENAMED Requirements
- FROM: `### Requirement: Textual MVP screens`
- TO: `### Requirement: Pygame MVP screens`

## MODIFIED Requirements
### Requirement: Pygame MVP screens
The system SHALL provide the MVP screens defined in the PRD using pygame rendering and event handling with keyboard-only navigation. The roster screen SHALL read from the session roster stored in `GameState` and rebuild its list rows on resume without reusing stale UI elements from the previous screen instance.

#### Scenario: Navigate from main menu to booking hub
- **WHEN** the player selects New Game on the main menu
- **THEN** the booking hub screen is shown

#### Scenario: Roster refresh after resume
- **WHEN** the user returns to the roster screen after leaving it
- **THEN** the roster list is rebuilt from the session roster without duplicate UI elements
