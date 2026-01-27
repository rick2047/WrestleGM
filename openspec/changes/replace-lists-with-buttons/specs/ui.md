## MODIFIED Requirements

### Requirement: Main Menu Navigation
The application SHALL present main menu options as individual, selectable buttons.

#### Scenario: Interacting with the Main Menu
- **WHEN** the user views the main menu screen
- **THEN** the options "New Game", "Load Game", and "Quit" MUST be rendered as distinct `Button` widgets.
- **AND** clicking one of these buttons MUST trigger the corresponding action.
- **AND** the button group MUST be centered and sized to feel intentional on large screens, rather than clustered in the top-left.

### Requirement: Standard Screen Layout
The application SHALL center standard screen body content by default to avoid top-left clustering on large screens.

#### Scenario: Viewing a standard screen
- **WHEN** the user views a screen built on the standard layout
- **THEN** the primary body content MUST be centered on the screen by default.

### Requirement: Game Hub Navigation
The application SHALL present game hub options as individual, selectable buttons.

#### Scenario: Interacting with the Game Hub
- **WHEN** the user views the game hub screen
- **THEN** the options "Book Current Show", "Roster Overview", and "Exit to Main Menu" MUST be rendered as distinct `Button` widgets.
- **AND** clicking one of these buttons MUST trigger the corresponding navigation event.
- **AND** the button group MUST be centered and sized to feel intentional on large screens, rather than clustered in the top-left.

### Requirement: Booking Hub Slot Selection
The application SHALL present booking hub slots as individual, selectable buttons.

#### Scenario: Interacting with the Booking Hub
- **WHEN** the user views the booking hub screen
- **THEN** each of the 5 show slots MUST be rendered as a distinct `Button` widget.
- **AND** clicking a slot button MUST navigate the user to the booking screen for that specific slot.
- **AND** the user MUST be able to move focus between slot buttons and the other booking hub actions using the same keyboard navigation patterns as before.
- **AND** the slot button layout MUST be centered and sized to feel intentional on large screens, rather than clustered in the top-left.
