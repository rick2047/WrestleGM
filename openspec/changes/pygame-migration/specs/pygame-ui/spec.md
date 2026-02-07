## ADDED Requirements

### Requirement: pygame UI package structure
The system SHALL organize pygame UI code in a dedicated package structure separate from Textual UI.

#### Scenario: Package organization
- **WHEN** the application starts
- **THEN** all pygame UI code is located in `wrestlegm/ui_pygame/`
- **AND** Textual UI code remains in `wrestlegm/ui/` untouched

### Requirement: Two-Tier Testing Strategy
The system SHALL implement two distinct types of UI tests: Screen Tests for visual regression and Flow Tests for interaction verification.

#### Scenario: Screen Tests - Visual Regression
- **WHEN** testing UI appearance
- **THEN** tests capture screen as PNG using Syrupy
- **AND** tests compare against baseline snapshot
- **AND** tests do NOT verify functionality
- **AND** one test exists per screen

#### Scenario: Flow Tests - Real Interaction
- **WHEN** testing UI functionality
- **THEN** tests simulate real pygame events (MOUSEBUTTONDOWN/UP)
- **AND** events flow through: pygame → UIManager → Screen → Router
- **AND** tests verify navigation and state changes
- **AND** tests do NOT compare visual output
- **AND** one test exists per user journey

### Requirement: Screen Test Implementation
The system SHALL implement visual regression tests using Syrupy PNGImageSnapshotExtension.

#### Scenario: Screen test setup
- **GIVEN** a headless pygame app with built screen
- **WHEN** test renders UI to surface
- **THEN** surface is captured as PNG bytes
- **AND** compared to baseline using snapshot_image fixture
- **AND** test fails if pixels differ

#### Scenario: Screen test coverage
- **WHEN** all screens are implemented
- **THEN** each screen has one snapshot test:
  - Main Menu
  - Save Slots
  - Game Hub
  - Booking Hub
  - Match Booking
  - Promo Booking
  - Wrestler Selection
  - Roster
  - Simulating
  - Results
  - Bankruptcy

#### Scenario: Screen test fixture
- **GIVEN** the app_with_built_screen fixture
- **THEN** it provides app with pre-built current screen
- **AND** screen is rendered with test data
- **AND** UI elements are created via screen.build()

### Requirement: Flow Test Implementation
The system SHALL implement interaction tests using real pygame event simulation.

#### Scenario: Flow test setup
- **GIVEN** a headless pygame app with interaction helpers
- **WHEN** test calls app.click(button)
- **THEN** MOUSEBUTTONDOWN event posted at button position
- **AND** MOUSEBUTTONUP event posted at same position
- **AND** events processed through UIManager
- **AND** UI_BUTTON_PRESSED event generated
- **AND** screen.handle_event() receives event

#### Scenario: Flow test coverage
- **WHEN** all user journeys are defined
- **THEN** each journey has one flow test:
  1. New Game Flow
  2. Load Game Flow
  3. Book a Match Flow
  4. Complete Show Flow
  5. Roster Inspection Flow
  6. Save and Quit Flow
  7. Bankruptcy Flow
  8. Back Navigation Flow
  9. Error Recovery Flow
  10. Cancel Navigation Flow

#### Scenario: Flow test fixture
- **GIVEN** the app_with_interaction fixture
- **THEN** it provides app.click(element) method
- **AND** it provides app.pump_events() method
- **AND** it tracks all events processed
- **AND** events flow through real code paths

### Requirement: Flow 1 - New Game
The system SHALL test the complete new game creation journey.

#### Scenario: New Game Flow Test
- **GIVEN** app is at Main Menu
- **WHEN** test clicks _new_game_button
- **THEN** navigates to SaveSlotSelectionScreen with mode=new
- **AND** screen is built (_slot_buttons is not None)
- **WHEN** test clicks _slot_buttons[0] (first empty slot)
- **THEN** navigates to GameHubScreen
- **AND** state.show_number is 1 (fresh game)
- **AND** screen is built (_booking_hub_button is not None)

### Requirement: Flow 2 - Load Game
The system SHALL test the complete game loading journey.

#### Scenario: Load Game Flow Test
- **GIVEN** app is at Main Menu
- **AND** a populated save exists in slot 2
- **WHEN** test clicks _load_game_button
- **THEN** navigates to SaveSlotSelectionScreen with mode=load
- **AND** occupied slots are clickable
- **WHEN** test clicks _slot_buttons[2] (occupied slot)
- **THEN** navigates to GameHubScreen
- **AND** state.show_number greater than 1 (not fresh game)
- **AND** loaded data matches original save

### Requirement: Flow 3 - Book Match
The system SHALL test the complete match booking journey.

#### Scenario: Book Match Flow Test
- **GIVEN** app is at Game Hub
- **WHEN** test clicks _booking_hub_button
- **THEN** navigates to BookingHubScreen
- **AND** 5 slot buttons are visible
- **WHEN** test clicks _slot_buttons[0] (empty match slot)
- **THEN** navigates to MatchBookingScreen
- **AND** category is singles, 2 wrestler slots visible
- **WHEN** test clicks _wrestler_slot_buttons[0]
- **THEN** navigates to WrestlerSelectionScreen
- **AND** roster list displayed
- **WHEN** test clicks _wrestler_buttons[0] (available wrestler)
- **THEN** navigates back to MatchBookingScreen
- **AND** wrestler slot 0 is populated
- **WHEN** test selects second wrestler and clicks _confirm_button
- **THEN** navigates to BookingHubScreen
- **AND** slot 0 shows match summary

### Requirement: Flow 4 - Complete Show
The system SHALL test the complete show cycle from booking to results.

#### Scenario: Complete Show Flow Test
- **GIVEN** app is at Game Hub with show N
- **WHEN** test navigates to Booking Hub
- **AND** books all 5 slots (3 matches + 2 promos)
- **THEN** _run_show_button is enabled (was disabled)
- **WHEN** test clicks _run_show_button
- **THEN** navigates to SimulatingScreen
- **AND** progress indicator animates
- **WHEN** simulation completes (auto-advance)
- **THEN** navigates to ResultsScreen
- **AND** show rating is displayed
- **AND** per-slot results shown
- **WHEN** test clicks _continue_button
- **THEN** navigates to GameHubScreen
- **AND** state.show_number is N+1
- **AND** state.money is updated

### Requirement: Flow 5 - Roster Inspection
The system SHALL test viewing wrestler details from roster.

#### Scenario: Roster Inspection Flow Test
- **GIVEN** app is at Game Hub
- **WHEN** test clicks _roster_button
- **THEN** navigates to RosterScreen
- **AND** scrollable wrestler list displayed
- **WHEN** test clicks _wrestler_panels[0] (first wrestler)
- **THEN** WrestlerInspectModal opens
- **AND** modal shows wrestler details (stats, rivalries)
- **WHEN** test clicks _close_button
- **THEN** modal closes
- **AND** back at RosterScreen

### Requirement: Flow 6 - Save and Quit
The system SHALL test saving game and reloading.

#### Scenario: Save and Quit Flow Test
- **GIVEN** app is at Game Hub with show number N
- **WHEN** test clicks _save_quit_button
- **THEN** game state is saved
- **AND** navigates to MainMenuScreen
- **WHEN** test clicks _load_game_button
- **AND** clicks slot 0 (where saved)
- **THEN** navigates to GameHubScreen
- **AND** state.show_number is N (preserved)
- **AND** all game data matches pre-save

### Requirement: Flow 7 - Bankruptcy
The system SHALL test bankruptcy detection and restart.

#### Scenario: Bankruptcy Flow Test
- **GIVEN** app has negative money
- **WHEN** app navigates to bankruptcy screen
- **THEN** BankruptcyScreen displays with warning
- **AND** _try_again_button is visible
- **WHEN** test clicks _try_again_button
- **THEN** navigates to GameHubScreen
- **AND** state.show_number is 1 (fresh)
- **AND** state.money is initial amount (positive)

### Requirement: Flow 8 - Back Navigation
The system SHALL testing using back button to return to previous screens.

#### Scenario: Back Navigation Flow Test
- **GIVEN** app is at Main Menu
- **WHEN** test clicks _new_game_button
- **THEN** navigates to SaveSlotSelectionScreen
- **WHEN** test clicks _back_button
- **THEN** navigates to MainMenuScreen
- **WHEN** test clicks _new_game_button
- **AND** clicks _slot_buttons[0]
- **THEN** navigates to GameHubScreen
- **WHEN** test clicks _booking_hub_button
- **THEN** navigates to BookingHubScreen
- **WHEN** test clicks _back_button
- **THEN** navigates to GameHubScreen

### Requirement: Flow 9 - Error Recovery
The system SHALL test graceful handling of corrupt saves.

#### Scenario: Error Recovery Flow Test
- **GIVEN** corrupt save exists in slot 2
- **AND** app is at Main Menu
- **WHEN** test clicks _load_game_button
- **THEN** navigates to SaveSlotSelectionScreen
- **WHEN** test clicks _slot_buttons[2] (corrupt slot)
- **THEN** ErrorModal displays with corrupt message
- **AND** app remains on SaveSlotSelectionScreen
- **WHEN** test clicks _ok_button on modal
- **THEN** modal closes
- **AND** still on SaveSlotSelectionScreen

### Requirement: Flow 10 - Cancel Navigation
The system SHALL test canceling navigation and returning.

#### Scenario: Cancel Navigation Flow Test
- **GIVEN** app is at Main Menu
- **WHEN** test clicks _new_game_button
- **THEN** navigates to SaveSlotSelectionScreen
- **WHEN** test clicks _back_button (cancel)
- **THEN** navigates back to MainMenuScreen
- **AND** no game was created

### Requirement: Main Menu screen
The system SHALL display a main menu with options for New Game, Load Game, and Quit.

#### Scenario: Display main menu
- **WHEN** the application launches
- **THEN** the Main Menu screen is displayed
- **AND** it shows three buttons: New Game, Load Game, Quit
- **AND** the screen follows the 4-zone layout (Header → Body → Actions → Footer)

#### Scenario: Navigate to save slots from main menu
- **WHEN** user clicks New Game button
- **THEN** the application navigates to Save Slot Selection screen in new mode

#### Scenario: Navigate to load game from main menu
- **WHEN** user clicks Load Game button
- **THEN** the application navigates to Save Slot Selection screen in load mode

#### Scenario: Quit from main menu
- **WHEN** user clicks Quit button
- **THEN** the application closes gracefully

### Requirement: Save Slot Selection screen
The system SHALL allow users to select a save slot for new or loaded games.

#### Scenario: Display save slots
- **WHEN** navigating to Save Slot Selection screen
- **THEN** it displays all available save slots with their status (empty/occupied)
- **AND** shows slot metadata (name, date if occupied)
- **AND** provides Back button to return to Main Menu

#### Scenario: Select slot for new game
- **GIVEN** the screen is in new mode
- **WHEN** user clicks an empty slot
- **THEN** the application creates a new game in that slot
- **AND** navigates to the Game Hub

#### Scenario: Select slot for loading
- **GIVEN** the screen is in load mode
- **WHEN** user clicks an occupied slot
- **THEN** the application loads the game from that slot
- **AND** navigates to the Game Hub

#### Scenario: Handle corrupt save
- **GIVEN** the screen is in load mode
- **WHEN** user clicks a slot with corrupt data
- **THEN** an error modal is displayed
- **AND** user remains on Save Slot Selection screen

### Requirement: Game Hub screen
The system SHALL provide a central hub for game navigation.

#### Scenario: Display game hub
- **WHEN** a game is loaded or created
- **THEN** the Game Hub screen displays
- **AND** shows options: Continue Game, Booking Hub, Roster View, Save & Quit
- **AND** displays current show number and money in header

#### Scenario: Navigate to booking hub
- **WHEN** user clicks Booking Hub
- **THEN** the application navigates to Booking Hub screen

#### Scenario: Navigate to roster view
- **WHEN** user clicks Roster View
- **THEN** the application navigates to Roster screen

#### Scenario: Save and quit
- **WHEN** user clicks Save & Quit
- **THEN** the current game state is saved
- **AND** the application returns to Main Menu

### Requirement: Booking Hub screen
The system SHALL display the current show card with all booked slots.

#### Scenario: Display booking hub
- **WHEN** navigating to Booking Hub
- **THEN** the screen displays all show slots (3 matches + 2 promos)
- **AND** shows summary for each slot (empty or booked content)
- **AND** displays current show cost in header
- **AND** displays current money in header

#### Scenario: Open match booking
- **GIVEN** a match slot is empty
- **WHEN** user clicks the slot
- **THEN** the application navigates to Match Booking screen for that slot

#### Scenario: Open promo booking
- **GIVEN** a promo slot is empty
- **WHEN** user clicks the slot
- **THEN** the application navigates to Promo Booking screen for that slot

#### Scenario: Edit existing match
- **GIVEN** a match slot has a booked match
- **WHEN** user clicks the slot
- **THEN** the application navigates to Match Booking screen with existing data pre-populated

#### Scenario: Run show validation
- **GIVEN** the show card is incomplete
- **WHEN** user attempts to run the show
- **THEN** the Run Show button is disabled
- **AND** a message indicates the show is incomplete

#### Scenario: Confirm run show
- **GIVEN** the show card is complete
- **WHEN** user clicks Run Show
- **THEN** a confirmation modal appears if cost exceeds money
- **AND** clicking Confirm navigates to Simulating screen

### Requirement: Match Booking screen
The system SHALL allow users to book a match with wrestlers and match type.

#### Scenario: Display match booking
- **WHEN** navigating to Match Booking screen
- **THEN** it displays:
  - Match category selector (singles, tag, etc.)
  - Match type selector
  - Wrestler selection slots (2-4 depending on category)
  - Cost breakdown
  - Rivalry indicators between selected wrestlers

#### Scenario: Change match category
- **WHEN** user selects a different match category
- **THEN** the number of wrestler slots updates accordingly
- **AND** match type options update to valid types for that category

#### Scenario: Select wrestler
- **WHEN** user clicks an empty wrestler slot
- **THEN** the application navigates to Wrestler Selection screen

#### Scenario: Validate duplicate wrestlers
- **GIVEN** two wrestler slots are filled
- **WHEN** user attempts to select the same wrestler for both slots
- **THEN** the selection is rejected with an error message

#### Scenario: Validate stamina
- **GIVEN** a wrestler has insufficient stamina
- **WHEN** user attempts to select that wrestler
- **THEN** the wrestler is shown as unavailable (grayed out)
- **AND** a message indicates low stamina

#### Scenario: Confirm booking
- **GIVEN** all required wrestlers are selected
- **WHEN** user clicks Confirm
- **THEN** the match is saved to the show card
- **AND** the application returns to Booking Hub

#### Scenario: Cancel booking
- **WHEN** user clicks Cancel
- **THEN** no changes are saved
- **AND** the application returns to Booking Hub

#### Scenario: Clear slot
- **GIVEN** a match exists in the slot
- **WHEN** user clicks Clear Slot
- **THEN** the slot is emptied
- **AND** the application returns to Booking Hub

### Requirement: Promo Booking screen
The system SHALL allow users to book a promo with a single wrestler.

#### Scenario: Display promo booking
- **WHEN** navigating to Promo Booking screen
- **THEN** it displays:
  - Single wrestler selection slot
  - Cost for the wrestler
  - Wrestler mic skill stat

#### Scenario: Select wrestler for promo
- **WHEN** user clicks the wrestler slot
- **THEN** the application navigates to Wrestler Selection screen

#### Scenario: Confirm promo booking
- **GIVEN** a wrestler is selected
- **WHEN** user clicks Confirm
- **THEN** the promo is saved to the show card
- **AND** the application returns to Booking Hub

### Requirement: Wrestler Selection screen
The system SHALL display a scrollable list of available wrestlers.

#### Scenario: Display wrestler list
- **WHEN** navigating to Wrestler Selection screen
- **THEN** it displays all roster wrestlers in a scrollable list
- **AND** shows for each wrestler:
  - Avatar (32x32)
  - Name
  - Popularity (stars)
  - Stamina (battery icon + value)
  - Cost
  - Alignment (Face/Heel)
  - Booking status indicator (if already booked)

#### Scenario: Filter unavailable wrestlers
- **GIVEN** some wrestlers are booked elsewhere or have low stamina
- **WHEN** the list is displayed
- **THEN** unavailable wrestlers are visually distinct (grayed out)
- **AND** a reason is shown (Booked, Low Stamina)

#### Scenario: Select wrestler
- **GIVEN** a wrestler is available
- **WHEN** user clicks the wrestler row
- **THEN** the wrestler is selected
- **AND** the application returns to the calling screen (Match/Promo Booking)

#### Scenario: Cancel selection
- **WHEN** user clicks Cancel
- **THEN** no wrestler is selected
- **AND** the application returns to the calling screen

### Requirement: Wrestler Inspect modal
The system SHALL allow viewing detailed wrestler information.

#### Scenario: Open inspect modal
- **GIVEN** the Wrestler Selection screen is open
- **WHEN** user clicks the inspect button on a wrestler
- **THEN** a modal displays full wrestler details:
  - Avatar (larger)
  - Name
  - Full stats (Pop, Sta, Mic)
  - Description
  - Active rivalries with other wrestlers

#### Scenario: Close inspect modal
- **WHEN** user clicks Close or outside the modal
- **THEN** the modal closes
- **AND** user returns to Wrestler Selection screen

### Requirement: Simulating screen
The system SHALL show simulation progress and transition to results.

#### Scenario: Display simulation
- **WHEN** navigating to Simulating screen
- **THEN** it displays a progress indicator
- **AND** shows Simulating Show #N text
- **AND** automatically advances when simulation completes

#### Scenario: Complete simulation
- **GIVEN** simulation is running
- **WHEN** all matches and promos are simulated
- **THEN** the application automatically navigates to Results screen

### Requirement: Results screen
The system SHALL display show results with match outcomes and ratings.

#### Scenario: Display results
- **WHEN** navigating to Results screen
- **THEN** it displays:
  - Overall show rating
  - Economy summary (audience, gate income, merch, total earned)
  - Per-slot results:
    - Match: Winner, losers, match type, rating
    - Promo: Wrestler, rating
  - Updated money amount

#### Scenario: Continue after results
- **WHEN** user clicks Continue
- **THEN** the show results are applied to roster stats
- **AND** the game is saved
- **AND** the application navigates to Game Hub

### Requirement: Roster screen
The system SHALL display the full roster for inspection.

#### Scenario: Display roster
- **WHEN** navigating to Roster screen
- **THEN** it displays all wrestlers in a scrollable list
- **AND** shows summary stats for each
- **AND** allows clicking to view full wrestler details

#### Scenario: View wrestler details from roster
- **WHEN** user clicks a wrestler
- **THEN** the Wrestler Inspect modal opens with full details

### Requirement: Bankruptcy screen
The system SHALL display when the promotion runs out of money.

#### Scenario: Display bankruptcy
- **GIVEN** money has reached 0 or below
- **WHEN** navigating to Bankruptcy screen
- **THEN** it displays bankruptcy message
- **AND** shows options: Try Again (restart), Main Menu

#### Scenario: Restart from bankruptcy
- **WHEN** user clicks Try Again
- **THEN** the game resets to initial state
- **AND** navigates to Booking Hub

### Requirement: Confirmation modals
The system SHALL provide confirmation dialogs for destructive actions.

#### Scenario: Confirm run show with debt
- **GIVEN** show cost exceeds current money
- **WHEN** user attempts to run show
- **THEN** a modal warns about going into debt
- **AND** shows Money: $X, Cost: $Y, Will debt: $Z
- **AND** provides Cancel and Confirm options

#### Scenario: Confirm clear slot
- **GIVEN** a slot has booked content
- **WHEN** user clicks Clear Slot
- **THEN** a confirmation modal appears
- **AND** asks Clear this slot?
- **AND** provides Cancel and Confirm options

### Requirement: Error modals
The system SHALL display error messages for invalid operations.

#### Scenario: Display error
- **GIVEN** an error occurs (e.g., corrupt save)
- **WHEN** the error is triggered
- **THEN** an error modal displays with the error message
- **AND** provides OK button to dismiss

### Requirement: Mouse-only interaction
The system SHALL support complete gameplay using only mouse/touch input.

#### Scenario: Navigate with mouse only
- **GIVEN** no keyboard is used
- **WHEN** user plays the game
- **THEN** all navigation is possible via clicking/tapping
- **AND** all buttons are touch-friendly (min 44x44dp)
- **AND** scrollable areas support touch scrolling

### Requirement: Mobile-friendly layout
The system SHALL use a mobile-first responsive layout.

#### Scenario: Layout on mobile device
- **GIVEN** the game runs on a mobile device
- **WHEN** displayed at 480x800 resolution
- **THEN** all UI elements are readable
- **AND** touch targets are at least 44x44dp
- **AND** text is 16px minimum for body, 24px for headers
- **AND** 32x32 pixel art displays crisply

#### Scenario: Layout scales to larger screens
- **GIVEN** the game runs on a tablet or desktop
- **WHEN** displayed at larger resolution
- **THEN** UI scales proportionally
- **AND** integer scaling preserves pixel art crispness
- **AND** letterboxing maintains aspect ratio if needed

### Requirement: Screen transitions
The system SHALL provide smooth transitions between screens.

#### Scenario: Fade transition
- **WHEN** navigating between screens
- **THEN** a fade transition occurs
- **AND** duration is 300ms (configurable)

### Requirement: pygame_gui integration
The system SHALL use pygame_gui for all UI elements.

#### Scenario: UI elements via pygame_gui
- **WHEN** any screen is displayed
- **THEN** all buttons use pygame_gui.UIButton
- **AND** all labels use pygame_gui.UILabel
- **AND** all containers use pygame_gui.core.UIContainer
- **AND** theming is applied via JSON theme file

### Requirement: Headless testing support
The system SHALL support headless testing for CI/CD.

#### Scenario: Run tests in CI
- **GIVEN** the CI environment has no display
- **WHEN** tests run with SDL_VIDEODRIVER=dummy
- **THEN** all UI tests execute successfully
- **AND** visual snapshots are generated deterministically

### Requirement: Syrupy snapshot testing
The system SHALL use Syrupy for visual regression testing.

#### Scenario: Generate UI snapshots
- **GIVEN** a screen is rendered
- **WHEN** snapshot test runs
- **THEN** the screen surface is captured as PNG
- **AND** compared against baseline using PNGImageSnapshotExtension
- **AND** tests fail if pixels differ

#### Scenario: Update snapshots
- **WHEN** running pytest --snapshot-update
- **THEN** all baseline PNG files are regenerated
- **AND** new baselines are committed to repository

### Requirement: Game state persistence
The system SHALL maintain save/load compatibility.

#### Scenario: Save game from pygame UI
- **GIVEN** a game is in progress
- **WHEN** save is triggered
- **THEN** the save format matches Textual UI format
- **AND** the save can be loaded by either UI version

#### Scenario: Load Textual save in pygame
- **GIVEN** a save was created in Textual UI
- **WHEN** loading in pygame UI
- **THEN** the game loads successfully
- **AND** all data is preserved correctly
