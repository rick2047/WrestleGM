## MODIFIED Requirements
### Requirement: Textual MVP screens
The system SHALL provide the MVP screens defined in the PRD using pygame rendering and input handling. The roster screen SHALL read from the session roster stored in `GameState` and rebuild its list rows on resume without reusing mounted widget IDs.

#### Scenario: Navigate from main menu to booking hub
- **WHEN** the player selects New Game on the main menu
- **THEN** the booking hub screen is shown

#### Scenario: Roster refresh after resume
- **WHEN** the user returns to the roster screen after leaving it
- **THEN** the roster list is rebuilt from the session roster without duplicate widget IDs
