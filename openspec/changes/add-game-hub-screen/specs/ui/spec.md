## ADDED Requirements
### Requirement: Main menu meta-only navigation
The system SHALL render a Main Menu that only offers New Game and Quit, and SHALL not expose gameplay screens while a session is active.

#### Scenario: Main menu mockup layout
- **WHEN** the Main Menu is displayed
- **THEN** it matches the following ASCII mockup:
```
┌──────────────────────────────────────┐
│ WrestleGM                            │
│ Main Menu                            │
├──────────────────────────────────────┤
│ ▸ New Game                           │
│                                      │
│   Quit                               │
│                                      │
├──────────────────────────────────────┤
│ ↑↓ Navigate   Enter Select           │
└──────────────────────────────────────┘
```

#### Scenario: Main menu options
- **WHEN** the Main Menu is shown
- **THEN** the only options are New Game and Quit

#### Scenario: Enter session from Main Menu
- **WHEN** the player selects New Game
- **THEN** a new session is initialized and the Game Hub is shown

### Requirement: Game hub screen
The system SHALL provide a Game Hub screen that displays the current show number and offers Book Current Show, Roster Overview, and Exit to Main Menu actions. The hub SHALL be the only gateway to gameplay screens and SHALL not run simulation or apply state changes. The show subtitle line under Book Current Show SHALL display the show name/number and be non-selectable text.

#### Scenario: Game hub mockup layout
- **WHEN** the Game Hub is displayed
- **THEN** it matches the following ASCII mockup:
```
┌──────────────────────────────────────┐
│ WrestleGM                            │
│ Game Hub                             │
├──────────────────────────────────────┤
│ ▸ Book Current Show                  │
│   Episode 12: Rising Tensions        │
│                                      │
│   Roster Overview                    │
│                                      │
│   Exit to Main Menu                  │
├──────────────────────────────────────┤
│ ↑↓ Navigate   Enter Select   Q Quit  │
└──────────────────────────────────────┘
```

#### Scenario: Show subtitle is descriptive
- **WHEN** the Game Hub is displayed
- **THEN** the show subtitle line is descriptive text and not a separate action

#### Scenario: Quit from Game Hub
- **WHEN** the player presses Q on the Game Hub
- **THEN** the application quits

#### Scenario: Enter hub after new game
- **WHEN** a new session is initialized
- **THEN** the Game Hub is shown with the current show number

#### Scenario: Navigate to booking from hub
- **WHEN** the player selects Book Current Show in the Game Hub
- **THEN** the booking hub screen is shown

#### Scenario: Navigate to roster from hub
- **WHEN** the player selects Roster Overview in the Game Hub
- **THEN** the roster screen is shown

#### Scenario: Exit to Main Menu from hub
- **WHEN** the player selects Exit to Main Menu in the Game Hub
- **THEN** the session ends and the Main Menu is shown

### Requirement: Results return to hub
The system SHALL return to the Game Hub after results and SHALL not provide roster or main menu shortcuts on the results screen.

#### Scenario: Continue after results
- **WHEN** the player selects Continue on the results screen
- **THEN** the Game Hub is shown

## MODIFIED Requirements
### Requirement: Textual MVP screens
The system SHALL provide the MVP screens defined in the PRD using Textual widgets and keyboard-only navigation. The roster screen SHALL read from the session roster stored in `GameState`, render the roster in a table with Name/Stamina/Popularity columns, include a header row naming the name/stamina/popularity columns, format rows as `{emoji} {name:<18} {sta:>3} {pop:>3}{fatigue}`, display alignment via emoji (Face 😃, Heel 😈), truncate names longer than 18 characters to 15 + `...`, and rebuild its list rows on resume without reusing mounted widget IDs.

#### Scenario: Navigate from main menu to game hub
- **WHEN** the player selects New Game on the main menu
- **THEN** the game hub screen is shown

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
The system SHALL use keyboard-only navigation and display a persistent footer that shows key bindings only. Enter SHALL activate the focused widget. Escape SHALL back out of the current screen or modal, except on the Game Hub where Escape has no effect. Arrow-key focus order SHALL skip disabled action buttons.

#### Scenario: Footer visibility
- **WHEN** any screen is shown
- **THEN** the footer is visible and displays only key bindings

#### Scenario: Arrow-key navigation across actions
- **WHEN** the user presses arrow keys on booking hub, match booking, results, or roster
- **THEN** focus can move from list views to the action buttons and back in a cycle

#### Scenario: Escape on Game Hub
- **WHEN** the player presses Escape on the Game Hub
- **THEN** no navigation occurs
