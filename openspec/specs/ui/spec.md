# ui Specification

## Purpose
TBD - created by archiving change add-wrestlegm-mvp. Update Purpose after archive.
## Requirements
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

### Requirement: Booking hub behavior
The system SHALL show five slots in fixed order (Match 1, Promo 1, Match 2, Promo 2, Match 3), allow slot selection, show match participant names with alignment emoji, show `Category · Stipulation` for match slots, and enable Run Show only when all slots are booked.

#### Scenario: Run Show enablement
- **WHEN** any slot is empty
- **THEN** Run Show is disabled

#### Scenario: Show category and type for matches
- **WHEN** the booking hub renders a booked match
- **THEN** it shows a `Category · Stipulation` line under the participant list

### Requirement: Match booking flow
The system SHALL edit matches in a dedicated booking screen, require confirmation before committing, and split match category selection (size) from stipulation selection (rules). The booking screen SHALL open after a category is chosen, render one wrestler row per required slot based on category, filter stipulations to those allowed for the selected category, allow changing stipulation via an inline dropdown, default the stipulation to the first available option when booking an empty slot, mark already-booked wrestlers with a 📅 indicator in the selection list, show popularity and stamina, display alignment via emoji (Face 😃, Heel 😈), render the selection list as a table with Name/Stamina/Popularity columns, include a header row naming the name/stamina/popularity columns, format rows as `{emoji} {name:<18} {sta:>3} {pop:>3}{fatigue}{booked_marker}`, and use 🥱 consistently for low-stamina indicators.

#### Scenario: Stipulation dropdown opens on Enter
- **WHEN** the user focuses the stipulation dropdown in match booking
- **AND WHEN** they press Enter
- **THEN** the stipulation dropdown opens without error

### Requirement: Booking validation in UI
The system SHALL block committing invalid matches and running invalid shows according to the booking rules.

#### Scenario: Prevent duplicate wrestler booking
- **WHEN** a wrestler is already booked in another slot
- **THEN** the UI marks them with a 📅 indicator and prevents selection with a ⛔ message

#### Scenario: Allow low-stamina promos
- **WHEN** a wrestler has stamina below `STAMINA_MIN_BOOKABLE`
- **THEN** the UI still allows selecting them for a promo slot

### Requirement: Results presentation
The system SHALL present match and promo results and the overall show rating using star ratings only, and SHALL include `Category · Stipulation` for match results.

#### Scenario: Show results after simulation
- **WHEN** the show completes
- **THEN** results list match winners and non-winners with star ratings, plus the overall show rating
- **AND THEN** match results include a `Category · Stipulation` line under the participants

### Requirement: Arrow-key navigation consistency
The system SHALL provide cyclical arrow-key navigation across all screens with focusable lists or action buttons.

#### Scenario: Cyclical focus traversal
- **WHEN** the user presses arrow keys on any screen with focusable lists or buttons
- **THEN** focus cycles from the last element back to the first and from the first back to the last

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
│   Show #12                           │
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

### Requirement: Promo booking flow
The system SHALL provide a promo booking screen that edits a single wrestler for a promo slot and requires confirmation before committing.

#### Scenario: Empty promo slot booking
- **WHEN** the user opens promo booking for an empty slot
- **THEN** the screen shows a single Wrestler field and a disabled Confirm action

#### Scenario: Confirm promo booking
- **WHEN** the user selects Confirm with a valid wrestler selected
- **THEN** a confirmation modal prompts for final confirmation before saving the slot

### Requirement: Shared wrestler selection for promos
The system SHALL reuse the existing wrestler selection screen for promo booking and may change only the contextual title text and validation rules needed to allow low-stamina promo selection.

#### Scenario: Promo wrestler selection layout
- **WHEN** the user opens wrestler selection from promo booking
- **THEN** the table layout, columns, and indicators match the match-booking selection screen

### Requirement: Mic skill visibility in roster and selection
The system SHALL display wrestler mic skill on the roster overview and wrestler selection screens using the same table layout.

#### Scenario: Mic skill column shown
- **WHEN** the roster overview or wrestler selection screen renders
- **THEN** the table includes a Mic column showing each wrestler's mic skill value

### Requirement: Match type selection screen
The system SHALL provide a match type selection screen when booking a match slot and use the selected match type to determine the required wrestler count in match booking.

#### Scenario: Match type selection
- **WHEN** the user selects a match slot on the booking hub
- **THEN** the match type selection screen lists Singles, Triple Threat, and Fatal 4-Way
- **AND THEN** selecting a match type opens match booking for that slot

### Requirement: Rivalry and cooldown emoji display
The system SHALL display rivalry and cooldown emojis on the match name line in the Booking Hub and Match Booking screens using the specified emoji mappings, and SHALL update the emoji list live as wrestlers are added or removed.

#### Scenario: Booking hub emojis
- **WHEN** a match slot is rendered in the Booking Hub
- **THEN** rivalry and cooldown emojis appear on the same line as the match name

#### Scenario: Match booking emojis
- **WHEN** the match booking screen has at least two wrestlers selected
- **THEN** rivalry and cooldown emojis appear on the match name line and update as selections change

### Requirement: Rivalry and cooldown emoji mapping and order
The system SHALL map rivalry levels to ⚡, 🔥, ⚔️, and 💥 for levels 1–4 respectively, map cooldown remaining shows to 🧊 (6–5), ❄️ (4–3), and 💧 (2–1), and order emojis by wrestler pair order derived from the booked wrestler list.

#### Scenario: Emoji mapping and ordering
- **WHEN** a match includes multiple rivalry or cooldown pairs
- **THEN** emojis are ordered by the unique pair order derived from the match wrestler list
- **AND THEN** each emoji uses the correct mapping for the pair's rivalry level or cooldown remaining shows

### Requirement: No rivalry emojis in show results
The system SHALL not display rivalry or cooldown emojis on the Show Results screen.

#### Scenario: Results omit rivalry emojis
- **WHEN** the Show Results screen renders
- **THEN** no rivalry or cooldown emojis are shown

