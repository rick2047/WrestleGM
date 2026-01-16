## MODIFIED Requirements
### Requirement: Main menu meta-only navigation
The system SHALL render a Main Menu that offers New Game, Load Game, and Quit, and SHALL not expose gameplay screens while a session is active.

#### Scenario: Main menu options include load game
- **WHEN** the Main Menu is shown
- **THEN** the only options are New Game, Load Game, and Quit

### Requirement: MVP screen list
The system SHALL provide the following MVP screens: Main Menu, Save Slot Selection, Game Hub, Booking Hub, Match Booking, Promo Booking, Wrestler Selection, Match Category Selection, Match Confirmation modal, Simulating Show, Show Results, Name Save Slot modal, Overwrite Save Slot modal, and Roster Overview.

#### Scenario: MVP screens are available
- **WHEN** the player navigates through the UI
- **THEN** each MVP screen is reachable via its expected flow

#### Scenario: Main menu mockup layout
- **WHEN** the Main Menu is displayed
- **THEN** it matches the Main Menu mockup in the ASCII mockups section

#### Scenario: Main menu options
- **WHEN** the Main Menu is shown
- **THEN** the only options are New Game, Load Game, and Quit

#### Scenario: Quit from Main Menu
- **WHEN** the player presses Q on the Main Menu
- **THEN** the application quits

#### Scenario: Enter session from Main Menu
- **WHEN** the player selects New Game
- **THEN** the Save Slot Selection screen is shown

- **WHEN** the player selects Load Game
- **THEN** the Save Slot Selection screen is shown

### Requirement: Game hub screen
The system SHALL provide a Game Hub screen that displays the current show number and offers Book Current Show, Roster Overview, and Exit to Main Menu actions. The hub SHALL be the gateway to gameplay screens once a session is active, except for the initial entry after creating or loading a save which MAY enter the Booking Hub directly. The show subtitle line under Book Current Show SHALL display the show name/number and be non-selectable text.

#### Scenario: Game hub mockup layout
- **WHEN** the Game Hub is displayed
- **THEN** it matches the Game Hub mockup in the ASCII mockups section

#### Scenario: Show subtitle is descriptive
- **WHEN** the Game Hub is displayed
- **THEN** the show subtitle line is descriptive text and not a separate action

#### Scenario: Quit from Game Hub
- **WHEN** the player presses Q on the Game Hub
- **THEN** the application quits

#### Scenario: Enter booking hub after new game
- **WHEN** a new session is initialized from an empty save slot
- **THEN** the Booking Hub is shown with the current show number

#### Scenario: Navigate to booking from hub
- **WHEN** the player selects Book Current Show in the Game Hub
- **THEN** the booking hub screen is shown

#### Scenario: Navigate to roster from hub
- **WHEN** the player selects Roster Overview in the Game Hub
- **THEN** the roster screen is shown

#### Scenario: Exit to Main Menu from hub
- **WHEN** the player selects Exit to Main Menu in the Game Hub
- **THEN** the session ends and the Main Menu is shown

## ADDED Requirements
### Requirement: Save slot selection screen
The system SHALL provide a Save Slot Selection screen that is shared by New Game and Load Game flows. The screen SHALL display exactly three slots with slot number, slot name when present, and last saved show number when present. Empty slots SHALL be disabled for Load Game. Selecting an empty slot in New Game SHALL proceed to Name Save Slot. Selecting a filled slot in New Game SHALL prompt for overwrite confirmation. Selecting a filled slot in Load Game SHALL load and navigate to the Booking Hub.

#### Scenario: Load game blocks empty slots
- **WHEN** the player selects an empty slot in Load Game mode
- **THEN** the selection is blocked

#### Scenario: New game empty slot naming
- **WHEN** the player selects an empty slot in New Game mode
- **THEN** the Name Save Slot modal is shown

#### Scenario: New game overwrite confirmation
- **WHEN** the player selects a filled slot in New Game mode
- **THEN** the Overwrite Save Slot modal is shown

#### Scenario: Load game from filled slot
- **WHEN** the player selects a filled slot in Load Game mode
- **THEN** the save is loaded and the Booking Hub is shown

### Requirement: Name save slot modal
The system SHALL provide a Name Save Slot modal that captures the slot name on first save. The Confirm action SHALL be disabled until a non-empty name is provided. Cancel SHALL return to Save Slot Selection without creating a game.

#### Scenario: Confirm requires a non-empty name
- **WHEN** the name field is empty or whitespace-only
- **THEN** Confirm is disabled

#### Scenario: Cancel returns to slot selection
- **WHEN** the player cancels naming a slot
- **THEN** the Save Slot Selection screen is shown and no game is created

### Requirement: Overwrite save slot modal
The system SHALL provide an Overwrite Save Slot modal when starting a new game on a filled slot. Confirm SHALL overwrite the existing slot and proceed to Name Save Slot. Cancel SHALL return to Save Slot Selection.

#### Scenario: Confirm overwrites and proceeds
- **WHEN** the player confirms overwrite
- **THEN** the slot is cleared and the Name Save Slot modal is shown

#### Scenario: Cancel returns to slot selection
- **WHEN** the player cancels overwrite
- **THEN** the Save Slot Selection screen is shown
