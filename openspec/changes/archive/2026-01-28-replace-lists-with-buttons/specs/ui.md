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

### Requirement: Save/Load Slot Selection
The application SHALL present save/load slots as individual, selectable buttons.

#### Scenario: Interacting with save/load slots
- **WHEN** the user views the save or load slot selection screen
- **THEN** each slot MUST be rendered as a distinct `Button` widget.
- **AND** clicking a slot button MUST trigger the same selection flow as the current list-based UI.
- **AND** when in load mode, slots without a saved game MUST be disabled or otherwise non-selectable.
- **AND** the slot button layout MUST be centered and sized to feel intentional on large screens, rather than clustered in the top-left.

### Requirement: Booking Hub Promo Alignment
The application SHALL display wrestler alignment emoji for promo slots on the booking hub.

#### Scenario: Viewing a promo slot
- **WHEN** the booking hub renders a promo slot with a booked wrestler
- **THEN** the slot summary MUST include the wrestler alignment emoji alongside their name.

### Requirement: Roster Inspect Behavior
The application SHALL allow inspecting a wrestler from the roster overview.

#### Scenario: Inspecting a roster entry
- **WHEN** the user presses the inspect action on the roster overview screen
- **THEN** the application MUST open a read-only wrestler inspection view for the highlighted wrestler.
- **AND** closing the inspection view MUST restore focus to the roster list at the previously highlighted row.
