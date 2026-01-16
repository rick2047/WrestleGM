# ui Specification

## Purpose
TBD - created by archiving change add-wrestlegm-mvp. Update Purpose after archive.
## Requirements
### Requirement: Textual MVP screens
The system SHALL provide the MVP screens defined in the PRD using Textual widgets and keyboard-only navigation. The roster screen SHALL read from the session roster stored in `GameState`, render the roster in a table with Name/Stamina/Mic/Popularity columns, include a header row naming the name/stamina/mic/popularity columns, format rows as `{emoji} {name:<18} {sta:>3} {mic:>3} {pop:>3}{fatigue}`, display alignment via emoji (Face 😃, Heel 😈), truncate names longer than 18 characters to 15 + `...`, and rebuild its list rows on resume without reusing mounted widget IDs.

#### Scenario: Navigate from main menu to game hub
- **WHEN** the player selects New Game on the main menu
- **THEN** the game hub screen is shown

#### Scenario: Roster refresh after resume
- **WHEN** the user returns to the roster screen after leaving it
- **THEN** the roster list is rebuilt from the session roster without duplicate widget IDs

#### Scenario: Roster header and row formatting
- **WHEN** the roster screen renders
- **THEN** a header row names the name, stamina, mic, and popularity columns
- **AND THEN** each roster row follows the format `{emoji} {name:<18} {sta:>3} {mic:>3} {pop:>3}{fatigue}`
- **AND THEN** wrestler names longer than 18 characters are truncated to 15 + `...`

#### Scenario: Roster alignment emoji mapping
- **WHEN** the roster screen renders
- **THEN** Face alignment uses 😃 and Heel alignment uses 😈

### Requirement: Global navigation keys and footer
The system SHALL use keyboard-only navigation and display a persistent footer that shows key bindings only. Enter SHALL activate the focused widget. Escape SHALL back out of the current screen or modal where a back action exists, except on the Game Hub, Main Menu, and Show Results screens where Escape has no effect. Arrow-key focus order SHALL skip disabled action buttons, loop between lists and action buttons, and wrap from last to first and first to last within a screen. Left/Right keys SHALL move between horizontal fields or buttons where applicable.

#### Scenario: Footer visibility
- **WHEN** any screen is shown
- **THEN** the footer is visible and displays only key bindings

#### Scenario: Arrow-key navigation across actions
- **WHEN** the user presses arrow keys on booking hub, match booking, results, or roster
- **THEN** focus can move from list views to the action buttons and back in a cycle

#### Scenario: Left/right navigation across buttons
- **WHEN** the user presses Left/Right on a screen with horizontal buttons
- **THEN** focus moves between those buttons

#### Scenario: Escape on Game Hub
- **WHEN** the player presses Escape on the Game Hub
- **THEN** no navigation occurs

#### Scenario: Escape on Main Menu
- **WHEN** the player presses Escape on the Main Menu
- **THEN** no navigation occurs

#### Scenario: Escape on Show Results
- **WHEN** the player presses Escape on the Show Results screen
- **THEN** no navigation occurs

### Requirement: Navigation stack behavior
The system SHALL push and pop screens on a navigation stack, pop on Escape where allowed, and preserve in-progress booking drafts while navigating into sub-screens.

#### Scenario: Escape pops the current screen
- **WHEN** the player presses Escape on a screen with a back action
- **THEN** the current screen is popped

#### Scenario: Subscreen selection returns
- **WHEN** the player selects a wrestler or match category
- **THEN** the selection screen is popped and control returns to the parent screen

#### Scenario: Draft state persists across subscreens
- **WHEN** the player opens wrestler selection or match category selection during booking
- **THEN** the in-progress draft remains intact when returning to booking

#### Scenario: Cancel discards draft
- **WHEN** the player cancels a booking screen
- **THEN** the in-progress draft is discarded without committing changes

### Requirement: Footer behavior
The system SHALL render a footer on all screens that displays key bindings only, updates based on focus, shows only modal bindings when a modal is open, and hides internal or non-action bindings.

#### Scenario: Footer shows key bindings only
- **WHEN** any screen is visible
- **THEN** the footer shows key bindings only and no game state or hints

#### Scenario: Footer is authoritative
- **WHEN** the player needs to discover available actions
- **THEN** the footer reflects the current available key bindings

#### Scenario: Footer updates for modals
- **WHEN** a modal is open
- **THEN** the footer shows only modal bindings

#### Scenario: Hidden bindings are excluded
- **WHEN** internal bindings exist
- **THEN** they do not appear in the footer

### Requirement: Visual indicator language
The system SHALL use a consistent emoji indicator language and alignment emojis in roster and booking views.

| Indicator | Meaning                                         | Blocks Action |
| --------- | ----------------------------------------------- | ------------- |
| ⛔         | Logical impossibility (e.g. duplicate wrestler) | Yes           |
| 🥱        | Low stamina / fatigued                          | Yes           |
| 📅        | Already booked in another slot                  | Yes           |

Alignment SHALL be shown by prefixing the wrestler name with Face 😃 or Heel 😈. Indicators rely on iconography first; color is supplemental.

#### Scenario: Alignment emoji usage
- **WHEN** wrestler names are rendered in roster or booking lists
- **THEN** they are prefixed with 😃 for Face and 😈 for Heel

#### Scenario: Blocked actions show ⛔
- **WHEN** an invalid selection is attempted
- **THEN** the UI displays a ⛔ indicator with a short inline message

#### Scenario: Empty slots show placeholders
- **WHEN** a booking field is empty or incomplete
- **THEN** it shows an `[ Empty ]` or `[ Unset ]` placeholder and the action is blocked

### Requirement: Validation philosophy
The system SHALL validate actions at commit time, block impossible states only, allow low-stamina wrestlers in promos, avoid advisory warnings beyond indicators and short inline errors, and avoid projections or odds in the UI.

#### Scenario: Block impossible states only
- **WHEN** a selection would create a duplicate or invalid booking
- **THEN** the UI blocks the action and shows the corresponding indicator

#### Scenario: No projections or advice
- **WHEN** the player is booking or reviewing results
- **THEN** the UI does not display odds, projections, or advisory hints

### Requirement: Booking hub behavior
The system SHALL show five slots in fixed order (Match 1, Promo 1, Match 2, Promo 2, Match 3), allow slot selection, show match participant names with alignment emoji, show `Category · Stipulation` for match slots, and enable Run Show only when all slots are booked.

#### Scenario: Run Show enablement
- **WHEN** any slot is empty
- **THEN** Run Show is disabled

#### Scenario: Run Show requires a valid card
- **WHEN** the show card has validation errors
- **THEN** Run Show is disabled

#### Scenario: Show category and type for matches
- **WHEN** the booking hub renders a booked match
- **THEN** it shows a `Category · Stipulation` line under the participant list

#### Scenario: Match participants display format
- **WHEN** a match slot is booked
- **THEN** the participant line uses alignment emojis and separates names with `vs`

#### Scenario: Enter opens slot editor
- **WHEN** the player selects a match slot
- **THEN** the match category selection screen opens

- **WHEN** the player selects a promo slot
- **THEN** the promo booking screen opens

#### Scenario: No partial slots on the card
- **WHEN** a slot is shown as booked in the booking hub
- **THEN** it contains a fully valid match or promo

#### Scenario: Back returns to Game Hub
- **WHEN** the player selects Back on the booking hub
- **THEN** the Game Hub is shown

### Requirement: Match booking flow
The system SHALL edit matches in a dedicated booking screen, require confirmation before committing, and split match category selection (size) from stipulation selection (rules). The booking screen SHALL open after a category is chosen, render one wrestler row per required slot based on category, filter stipulations to those allowed for the selected category, allow changing stipulation via an inline dropdown, default the stipulation to the first available option when booking an empty slot, mark already-booked wrestlers with a 📅 indicator in the selection list, show popularity and stamina, display alignment via emoji (Face 😃, Heel 😈), render the selection list as a table with Name/Stamina/Mic/Popularity columns, include a header row naming the name/stamina/mic/popularity columns, truncate names longer than 18 characters to 15 + `...`, format rows as `{emoji} {name:<18} {sta:>3} {mic:>3} {pop:>3}{fatigue}{booked_marker}`, and use 🥱 consistently for low-stamina indicators.

#### Scenario: Stipulation dropdown opens on Enter
- **WHEN** the user focuses the stipulation dropdown in match booking
- **AND WHEN** they press Enter
- **THEN** the stipulation dropdown opens without error

#### Scenario: Match booking opens after category selection
- **WHEN** the player selects a match category
- **THEN** match booking opens for that slot

#### Scenario: Re-selecting a match category keeps early picks
- **WHEN** the player re-selects a match category with fewer required slots
- **THEN** the earliest selected wrestlers remain assigned and any extra slots are cleared

#### Scenario: Re-selecting a match category adds new slots
- **WHEN** the player re-selects a match category with more required slots
- **THEN** the existing selected wrestlers remain assigned and new empty slots are added

#### Scenario: Confirm disabled until valid
- **WHEN** the match booking screen has incomplete or invalid selections
- **THEN** the Confirm action is disabled

#### Scenario: Clear Slot availability
- **WHEN** the match slot is empty
- **THEN** Clear Slot is disabled

#### Scenario: Cancel returns to match category selection
- **WHEN** the player selects Cancel or presses Escape in match booking
- **THEN** they return to match category selection without committing changes

#### Scenario: Draft selections show booked marker
- **WHEN** the wrestler selection screen is opened during match booking
- **THEN** wrestlers already selected in the current draft show a 📅 marker

#### Scenario: Clear Slot returns to booking hub
- **WHEN** the player clears a booked match slot
- **THEN** the slot is emptied and the booking hub is shown

#### Scenario: Stipulation list filters by category
- **WHEN** a match category is selected
- **THEN** the stipulation list includes only stipulations allowed for that category

#### Scenario: Default stipulation for empty slots
- **WHEN** the player books an empty match slot
- **THEN** the stipulation defaults to the first available option

### Requirement: Match booking confirmation modal
The system SHALL confirm match booking via a modal overlay with the prompt `Confirm booking?`, explicit Confirm/Cancel actions, and trapped focus.

#### Scenario: Confirmation modal prompt
- **WHEN** the confirmation modal is displayed
- **THEN** it shows the prompt `Confirm booking?`

#### Scenario: Confirmation modal focus trap
- **WHEN** the confirmation modal is open
- **THEN** focus is trapped inside the modal and the background is non-interactive

### Requirement: Booking validation in UI
The system SHALL block committing invalid matches and running invalid shows according to the booking rules.

#### Scenario: Prevent duplicate wrestler booking
- **WHEN** a wrestler is already booked in another slot
- **THEN** the UI marks them with a 📅 indicator and prevents selection with a ⛔ message

#### Scenario: Allow low-stamina promos
- **WHEN** a wrestler has stamina below `STAMINA_MIN_BOOKABLE`
- **THEN** the UI still allows selecting them for a promo slot

#### Scenario: Block low-stamina match booking
- **WHEN** a wrestler has stamina at or below `STAMINA_MIN_BOOKABLE` and the player is booking a match
- **THEN** the UI prevents selection with a ⛔ message

#### Scenario: Prevent partial slot commits
- **WHEN** required booking fields are incomplete
- **THEN** the UI prevents committing the slot

#### Scenario: Prevent duplicates within a match
- **WHEN** the player selects a wrestler already chosen in the same match
- **THEN** the UI blocks the selection with a ⛔ message

### Requirement: Results presentation
The system SHALL present match and promo results and the overall show rating using star ratings only with half-star precision, and SHALL include `Category · Stipulation` for match results.

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

### Requirement: Results return to hub
The system SHALL return to the Game Hub after results and SHALL not provide roster or main menu shortcuts on the results screen.

#### Scenario: Continue after results
- **WHEN** the player selects Continue on the results screen
- **THEN** the Game Hub is shown

### Requirement: Simulating screen behavior
The system SHALL present a Simulating screen that runs `GameState.run_show()` on entry, accepts no input, and automatically advances to the Results screen after a short delay.

#### Scenario: Simulate and advance
- **WHEN** the Simulating screen is shown
- **THEN** the show is run and the Results screen appears automatically

#### Scenario: Simulating screen ignores input
- **WHEN** the Simulating screen is active
- **THEN** user input is ignored

### Requirement: Promo booking flow
The system SHALL provide a promo booking screen that edits a single wrestler for a promo slot and requires confirmation before committing.

#### Scenario: Empty promo slot booking
- **WHEN** the user opens promo booking for an empty slot
- **THEN** the screen shows a single Wrestler field and a disabled Confirm action

#### Scenario: Promo wrestler field opens selection
- **WHEN** the player activates the Wrestler field
- **THEN** the wrestler selection screen opens

#### Scenario: Confirm promo booking
- **WHEN** the user selects Confirm with a valid wrestler selected
- **THEN** a confirmation modal prompts for final confirmation before saving the slot

#### Scenario: Clear Slot availability for promos
- **WHEN** the promo slot is empty
- **THEN** Clear Slot is disabled

#### Scenario: Clear promo returns to booking hub
- **WHEN** the player clears a booked promo slot
- **THEN** the slot is emptied and the booking hub is shown

#### Scenario: Cancel promo booking
- **WHEN** the player cancels promo booking
- **THEN** changes are discarded and the booking hub is shown

### Requirement: Shared wrestler selection for promos
The system SHALL reuse the existing wrestler selection screen for promo booking and may change only the contextual title text and validation rules needed to allow low-stamina promo selection.

#### Scenario: Promo wrestler selection layout
- **WHEN** the user opens wrestler selection from promo booking
- **THEN** the table layout, columns, and indicators match the match-booking selection screen

### Requirement: Wrestler selection screen layout
The system SHALL render a wrestler selection table with Name/Sta/Mic/Pop columns, an inline message row for blocking errors, and Select/Cancel actions.

#### Scenario: Wrestler selection components
- **WHEN** the wrestler selection screen renders
- **THEN** it shows the table, inline message row, and Select/Cancel actions

### Requirement: Mic skill visibility in roster and selection
The system SHALL display wrestler mic skill on the roster overview and wrestler selection screens using the same table layout.

#### Scenario: Mic skill column shown
- **WHEN** the roster overview or wrestler selection screen renders
- **THEN** the table includes a Mic column showing each wrestler's mic skill value

### Requirement: Match category selection screen
The system SHALL provide a match category selection screen when booking a match slot and use the selected category to determine the required wrestler count in match booking.

#### Scenario: Match category selection
- **WHEN** the user selects a match slot on the booking hub
- **THEN** the match category selection screen lists Singles, Triple Threat, and Fatal 4-Way
- **AND THEN** selecting a match category opens match booking for that slot

#### Scenario: Match category actions
- **WHEN** the match category selection screen is shown
- **THEN** Select and Cancel actions are available

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

### Requirement: Microcopy and tone rules
The system SHALL use neutral, observational language, avoid system explanations or advice, and use "def." instead of "defeated" in match results.

#### Scenario: Match results use "def."
- **WHEN** match results are shown
- **THEN** the winner line uses "def."

### Requirement: UX guarantees
The system SHALL provide keyboard-only interaction, deterministic behavior, no accidental exits, and require explicit player intent for progression.

#### Scenario: No accidental exits
- **WHEN** the player presses Escape on screens without a back action
- **THEN** no navigation occurs

### Requirement: Widget mapping
The system SHALL map each screen to the following primary Textual widgets.

| Screen               | Primary Widgets             |
| -------------------- | --------------------------- |
| Main Menu            | ListView, Static, Footer    |
| Game Hub             | ListView, Static, Footer    |
| Booking Hub          | ListView, Static, Button    |
| Match Booking        | ListView, Select, Static, Button |
| Promo Booking        | ListView, Static, Button    |
| Wrestler Selection   | DataTable, Static, Button   |
| Match Category Selection | ListView, Static, Button    |
| Confirmation         | ModalScreen, Static, Button |
| Simulating           | Static, Footer              |
| Results              | Static, Button, Footer      |
| Roster               | DataTable, Static, Button   |

#### Scenario: Widget usage
- **WHEN** a screen is implemented
- **THEN** it uses the primary widgets listed for that screen

### Requirement: ASCII mockups
The system SHALL match the following ASCII mockups for the MVP screens.

#### Scenario: Screen layouts follow mockups
- **WHEN** an MVP screen is displayed
- **THEN** it matches the corresponding ASCII mockup

#### Main Menu
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

#### Game Hub
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

#### Booking Hub (Slot-Level)
```
┌──────────────────────────────────────┐
│ WrestleGM                            │
│ Show #12                             │
├──────────────────────────────────────┤
│ ▸ Match 1                            │
│   😃 Kenny Omega vs 😈 Eddie Kingston │
│   Singles · Hardcore                 │
│                                      │
│   Promo 1                            │
│   Jon Moxley                         │
│                                      │
│   Match 2                            │
│   😈 Jon Moxley vs 😃 Claudio vs 😃 Kenny │
│   Triple Threat · Submission         │
│                                      │
│   Promo 2                            │
│   [ Empty ]                          │
│                                      │
│   Match 3                            │
│   [ Empty ]                          │
│                                      │
├──────────────────────────────────────┤
│ [ Run Show ] (disabled)              │
│ [ Back ]                             │
└──────────────────────────────────────┘
```

#### Match Booking (Empty Slot)
```
┌──────────────────────────────────────┐
│ Book Match 3                         │
│ Singles                              │
├──────────────────────────────────────┤
│ ▸ [ Empty ]                          │
│                                      │
│   [ Empty ]                          │
│                                      │
│   Stipulation                        │
│   [ Hardcore ▾ ]                     │
│                                      │
├──────────────────────────────────────┤
│ [ Confirm ] (disabled)               │
│ [ Clear Slot ] (disabled)            │
│ [ Cancel ]                           │
└──────────────────────────────────────┘
```

#### Match Booking (Filled Slot)
```
┌──────────────────────────────────────┐
│ Book Match 3                         │
│ Singles                              │
├──────────────────────────────────────┤
│ ▸ 😃 Kenny Omega                     │
│                                      │
│   😈 Eddie Kingston                  │
│                                      │
│   Stipulation                        │
│   Submission                         │
│                                      │
├──────────────────────────────────────┤
│ [ Confirm ]                          │
│ [ Clear Slot ]                       │
│ [ Cancel ]                           │
└──────────────────────────────────────┘
```

#### Promo Booking (Filled Slot)
```
┌──────────────────────────────────────┐
│ Book Promo 1                         │
│ Jon Moxley                           │
├──────────────────────────────────────┤
│ ▸ Wrestler                           │
│   Jon Moxley                         │
│                                      │
├──────────────────────────────────────┤
│ [ Confirm ]                          │
│ [ Clear Slot ]                       │
│ [ Cancel ]                           │
└──────────────────────────────────────┘
```

#### Wrestler Selection
```
Select Wrestler (Match 3 · A)

| Name                 | Sta | Mic | Pop |
| -------------------- | --- | --- | ---:|
| 😃 Kenny Omega       |  28 |  88 |  92 🥱 📅 |
| 😈 Jon Moxley        |  12 |  86 |  88 🥱   |
| 😃 Eddie Kingston    |  64 |  70 |  74     |

⛔ Already booked in Match 2

[ Select ]   [ Cancel ]
```

#### Match Category Selection
```
┌──────────────────────────────────────┐
│ Select Match Category                │
├──────────────────────────────────────┤
│ ▸ Singles                            │
│                                      │
│   Triple Threat                      │
│                                      │
│   Fatal 4-Way                        │
├──────────────────────────────────────┤
│ [ Select ]   [ Cancel ]              │
└──────────────────────────────────────┘
```

#### Match Booking Confirmation (Modal)
```
              ┌──────────────────────┐
              │ Confirm booking?     │
              ├──────────────────────┤
              │ [ Confirm ]          │
              │ [ Cancel ]           │
              └──────────────────────┘
```

#### Show Results
```
┌────────────────────────── SHOW RESULTS ──────────────────────────┐
│ WrestleGM                                                        │
│ Show #12 · RAW                                                   │
├──────────────────────────────────────────────────────────────────┤
│ Match 1                                                         │
│ 😃 Kenny Omega def. 😈 Eddie Kingston                            │
│ Singles · Hardcore                                               │
│                                                          ★★★☆☆ │
│                                                                  │
│ Promo 1                                                         │
│ Jon Moxley                                                      │
│                                                          ★★☆☆☆ │
│                                                                  │
│ Match 2                                                         │
│ 😈 Jon Moxley def. 😃 Claudio Castagnoli                          │
│ Singles · Submission                                             │
│                                                          ★★★★☆ │
│                                                                  │
│ Promo 2                                                         │
│ Maria Blaze                                                     │
│                                                          ★★☆☆☆ │
│                                                                  │
│ Match 3                                                         │
│ 😃 Alpha def. 😈 Beta, 😃 Gamma                                   │
│ Triple Threat · High Flying                                      │
│                                                          ★★★☆☆ │
├──────────────────────────────────────────────────────────────────┤
│ Show Rating: ★★★½☆                                             │
│                                                                  │
│ [ Continue ]                                                    │
└──────────────────────────────────────────────────────────────────┘
```

#### Roster Overview
```
Roster Overview

| Name                   | Sta | Mic | Pop |
| ---------------------- | --- | --- | ---:|
| 😃 Kenny Omega         |  28 |  88 |  89  |
| 😈 Jon Moxley          |  12 |  86 |  82 🥱 |
| 😃 Eddie Kingston      |  64 |  70 |  74  |
| 😃 Claudio Castagnoli  |  71 |  75 |  77  |

[ Back ]
```

### Requirement: Save slot selection screen
The system SHALL provide a Save Slot Selection screen that is shared by New Game and Load Game flows. The screen SHALL display exactly three slots with slot number, slot name when present, and the next show number to be played (derived from the last saved show index). Empty slots SHALL be disabled for Load Game. Selecting an empty slot in New Game SHALL proceed to Name Save Slot. Selecting a filled slot in New Game SHALL prompt for overwrite confirmation. Selecting a filled slot in Load Game SHALL load and navigate to the Booking Hub.

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
The system SHALL provide a Name Save Slot modal that captures the slot name on first save. The Confirm action SHALL be disabled until a non-empty name is provided. Cancel SHALL return to Save Slot Selection without creating a game. When invoked after an overwrite confirmation, the name field SHALL be pre-filled with the previous slot name.

#### Scenario: Confirm requires a non-empty name
- **WHEN** the name field is empty or whitespace-only
- **THEN** Confirm is disabled

#### Scenario: Cancel returns to slot selection
- **WHEN** the player cancels naming a slot
- **THEN** the Save Slot Selection screen is shown and no game is created

#### Scenario: Overwrite pre-fills name
- **WHEN** the Name Save Slot modal follows an overwrite confirmation
- **THEN** the input field is pre-filled with the overwritten slot name

### Requirement: Overwrite save slot modal
The system SHALL provide an Overwrite Save Slot modal when starting a new game on a filled slot. Confirm SHALL overwrite the existing slot and proceed to Name Save Slot. Cancel SHALL return to Save Slot Selection.

#### Scenario: Confirm overwrites and proceeds
- **WHEN** the player confirms overwrite
- **THEN** the Name Save Slot modal is shown and the existing save is retained until a new name is confirmed

#### Scenario: Cancel returns to slot selection
- **WHEN** the player cancels overwrite
- **THEN** the Save Slot Selection screen is shown

### Requirement: Load error feedback
The system SHALL show a modal error message when loading a save fails due to missing, corrupt, or unsupported save files.

#### Scenario: Load failure shows error
- **WHEN** a load attempt fails
- **THEN** an error modal explains the failure and returns the player to Save Slot Selection

