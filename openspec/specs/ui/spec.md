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

### Requirement: Centralized navigation routing
The system SHALL centralize screen navigation in the app layer using named routes so screens do not import each other directly.

#### Scenario: Screen transitions use the router
- **WHEN** a screen triggers navigation (e.g., Main Menu → Save Slots, Booking Hub → Match Category)
- **THEN** the transition is performed via a named route in the app router

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
The system SHALL edit matches in a dedicated booking screen with a single card layout, require confirmation before committing, allow selecting the wrestler count inline, render participants as a vertical list of Wrestler Views, filter stipulations by the selected wrestler count, and keep validation rules unchanged. The match booking screen SHALL show a rivalry summary header, allow changing stipulation via an inline dropdown, default the stipulation to the first available option when booking an empty slot, and keep Clear Slot/Cancel behavior consistent with current booking flows.

#### Scenario: Inline wrestler count selection
- **WHEN** the match booking screen is shown
- **THEN** the user can select the required wrestler count inline without opening a separate category screen

#### Scenario: Wrestler views in match booking
- **WHEN** the match booking screen renders
- **THEN** each participant slot is a Wrestler View card in a vertical scroll list

#### Scenario: Stipulation filtering
- **WHEN** a wrestler count is selected
- **THEN** the stipulation list includes only stipulations allowed for the derived match category

#### Scenario: Confirm disabled until valid
- **WHEN** the match booking screen has incomplete or invalid selections
- **THEN** the Confirm action is disabled

#### Scenario: Clear Slot availability
- **WHEN** the match slot is empty
- **THEN** Clear Slot is disabled

#### Scenario: Cancel returns to booking hub
- **WHEN** the player cancels match booking
- **THEN** they return to the booking hub without committing changes

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
The system SHALL provide the MVP screens defined in the PRD, including the startup guard screen for insufficient viewport size.

#### Scenario: MVP screens are available
- **WHEN** the app is running at or above the minimum viewport
- **THEN** the main menu, game hub, booking hub, match booking, promo booking, wrestler selection, results, and roster screens are available

#### Scenario: Guard screen availability
- **WHEN** the app is started in a terminal smaller than 60x30
- **THEN** the guard screen is shown in place of the normal UI

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
The system SHALL provide a promo booking screen that edits a single wrestler for a promo slot, renders the wrestler slot as a Wrestler View, disallows rivalry blocks in this context, and requires confirmation before committing.

#### Scenario: Empty promo slot booking
- **WHEN** the user opens promo booking for an empty slot
- **THEN** the screen shows a single Wrestler View and a disabled Confirm action

#### Scenario: Promo wrestler field opens selection
- **WHEN** the player activates the Wrestler View
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
The system SHALL reuse the wrestler selection screen for promo booking with contextual title text and validation rules that allow low-stamina promo selection, and SHALL keep the inspection modal available.

#### Scenario: Promo wrestler selection layout
- **WHEN** the user opens wrestler selection from promo booking
- **THEN** the table layout, columns, indicators, and inspection modal match match-booking selection behavior

### Requirement: Wrestler selection screen layout
The system SHALL render a wrestler selection table with Name, Pop, Sta, Mic, and Align columns, an inline message row for blocking errors, Select/Cancel actions, and an inspect hint for the `i` key.

#### Scenario: Wrestler selection components
- **WHEN** the wrestler selection screen renders
- **THEN** it shows the table, inline message row, Select/Cancel actions, and an inspect hint

### Requirement: Mic skill visibility in roster and selection
The system SHALL display wrestler mic skill on the roster overview and wrestler selection screens using the same table layout.

#### Scenario: Mic skill column shown
- **WHEN** the roster overview or wrestler selection screen renders
- **THEN** the table includes a Mic column showing each wrestler's mic skill value

### Requirement: Rivalry and cooldown emoji display
The system SHALL display rivalry and cooldown emojis on the match name line in the Booking Hub, and SHALL display an aggregated rivalry summary in the Match Booking header along with compact rivalry badges within Wrestler Views. Wrestler View rivalry badges SHALL reflect only rivalries between the displayed wrestler and other participants in the current match.

#### Scenario: Booking hub emojis
- **WHEN** a match slot is rendered in the Booking Hub
- **THEN** rivalry and cooldown emojis appear on the same line as the match name

#### Scenario: Match booking emojis
- **WHEN** the match booking screen has at least two wrestlers selected
- **THEN** the header shows the rivalry summary and each Wrestler View shows compact rivalry badges

### Requirement: Rivalry and cooldown emoji mapping and order
The system SHALL map rivalry levels to ⚡, 🔥, ⚔️, and 💥 for levels 1–4 respectively, map cooldown remaining shows to 🧊 (6–5), ❄️ (4–3), and 💧 (2–1), and SHALL aggregate match booking header emojis across unordered wrestler pairs using ASCII `xN` compression.

#### Scenario: Emoji mapping and ordering
- **WHEN** rivalries or cooldowns are displayed
- **THEN** each emoji uses the correct mapping for the pair's rivalry level or cooldown remaining shows
- **AND THEN** the match booking header aggregates across unordered pairs using ASCII `xN` counts

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

| Screen               | Primary Widgets                  |
| -------------------- | -------------------------------- |
| Main Menu            | ListView, Static, Footer         |
| Game Hub             | ListView, Static, Footer         |
| Booking Hub          | ListView, Static, Button         |
| Match Booking        | ListView, Select, Static, Button |
| Promo Booking        | ListView, Static, Button         |
| Wrestler Selection   | DataTable, Static, Button        |
| Wrestler Inspect Modal | ModalScreen, Static, Button     |
| Confirmation         | ModalScreen, Static, Button      |
| Simulating           | Static, Footer                   |
| Results              | Static, Button, Footer           |

#### Scenario: Widget usage
- **WHEN** each screen renders
- **THEN** it uses the primary widgets specified in the mapping

### Requirement: ASCII mockups
The system SHALL match the following ASCII mockups for the MVP screens relevant to booking and wrestler inspection.

#### Scenario: Match booking mockup layout
- **WHEN** the Match Booking screen renders
- **THEN** it matches the following layout:

```
┌──────────────────────────────────────────────┐
│ Match #1        🔥 x1                         │
├──────────────────────────────────────────────┤
│ [ 2 ▾ ]    [ Singles ▾ ]                      │
│                                              │
│ Wrestlers (VerticalScroll)                    │
│  ▶ 😃 Kazuchika Okada                         │
│    ┌───────────────┐                         │
│    │  avatar.png   │                         │
│    │ (half render) │                         │
│    └───────────────┘                         │
│    ⭐92  🔋28  🎤88                            │
│    🔥                                        │
│                                              │
│    😈 Jay White                               │
│    ┌───────────────┐                         │
│    │  avatar.png   │                         │
│    │ (half render) │                         │
│    └───────────────┘                         │
│    ⭐85  🔋40  🎤70                            │
│    🔥                                        │
│                                              │
│ [ Clear Slot ]   [ Confirm ]   [ Back ]       │
└──────────────────────────────────────────────┘
```

#### Scenario: Promo booking mockup layout
- **WHEN** the Promo Booking screen renders
- **THEN** it matches the following layout:

```
┌──────────────────────────────────────────────┐
│ Promo Slot #2                                 │
├──────────────────────────────────────────────┤
│ Performer                                     │
│  ▶ 😃 Kazuchika Okada                         │
│    ┌───────────────┐                         │
│    │  avatar.png   │                         │
│    │ (half render) │                         │
│    └───────────────┘                         │
│    ⭐92  🔋28  🎤88                            │
│                                              │
│ [ Clear Slot ]   [ Confirm ]   [ Back ]       │
└──────────────────────────────────────────────┘
```

#### Scenario: Wrestler selection inspect modal mockup
- **WHEN** the user opens inspection from wrestler selection
- **THEN** it matches the following layout:

```
┌──────────────────────────────────────────────┐
│ Select Wrestler                               │
├──────────────────────────────────────────────┤
│ Name            ⭐   🔋   🎤   Align            │
│ ▶ Okada           92   28   88   😃            │
│   Jay White       85   40   70   😈            │
│   Naito           88   35   82   😃            │
│   Omega           90   30   85   😃            │
│                                              │
│ ┌──────────────────────────────────────────┐ │
│ │ Wrestler Details                          │ │
│ │ 😃 Kazuchika Okada                        │ │
│ │ ──────────────────────────────────────── │ │
│ │ ┌───────────────┐                        │ │
│ │ │  avatar.png   │                        │ │
│ │ │ (half render) │                        │ │
│ │ └───────────────┘                        │ │
│ │ ⭐92  🔋28  🎤88                          │ │
│ │ "Ace of the Rainmaker..."                │ │
│ │                                          │ │
│ │ Rivalries                                 │ │
│ │  💥 Kenny Omega                           │ │
│ │  ⚔️ Tetsuya Naito                         │ │
│ │  🔥 Jay White                             │ │
│ │                                          │ │
│ │              [ Esc to close ]             │ │
│ └──────────────────────────────────────────┘ │
└──────────────────────────────────────────────┘
```

#### Scenario: Guard screen mockup
- **WHEN** the guard screen is shown
- **THEN** it matches the following layout:

```
┌──────────────────────────────────────────────┐
│                                              │
│   Terminal size too small (need 60x30).       │
│   Resize your terminal and restart the app.  │
│                                              │
│                [ Q ] Quit                    │
│                                              │
└──────────────────────────────────────────────┘
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

### Requirement: Modular UI organization
The UI implementation SHALL be organized into a package that separates the app entry point, screen modules, reusable widgets, and shared formatting helpers.

#### Scenario: Screen modules are isolated
- **WHEN** a developer opens a specific screen implementation
- **THEN** the screen logic lives in a dedicated module under `wrestlegm/ui/screens/`

#### Scenario: Widgets are reusable and screen-agnostic
- **WHEN** a custom widget is shared across multiple screens
- **THEN** it lives under `wrestlegm/ui/widgets/` and does not depend on game-state globals

#### Scenario: Stable public imports
- **WHEN** external code imports `WrestleGMApp` or screen classes from `wrestlegm.ui`
- **THEN** those imports remain valid via package re-exports

### Requirement: Externalized UI styling
The Textual app SHALL load its CSS from a `.tcss` file to keep styling separate from screen logic.

#### Scenario: CSS path configuration
- **WHEN** the app starts
- **THEN** `WrestleGMApp` loads styling via `CSS_PATH` pointing at the UI stylesheet

### Requirement: Minimum viewport guard screen
The system SHALL enforce a minimum terminal viewport of 60 columns by 30 rows at startup. If the terminal is smaller than 60x30 at startup, the system SHALL replace the normal UI with a non-interactive guard screen that only allows quitting the application.

#### Scenario: Guard screen shown on small viewport
- **WHEN** the app starts in a terminal smaller than 60x30
- **THEN** the guard screen is shown with a Quit action and no other UI elements

### Requirement: Wrestler View component
The system SHALL provide a reusable Wrestler View component that is built from configurable blocks (avatar, header, stats, description, rivalry) and renders in fixed height. Callers MUST explicitly enable or disable each block; absence of a block MUST NOT affect layout stability of the others.

#### Scenario: Wrestler View block configuration
- **WHEN** a Wrestler View is instantiated
- **THEN** each block is rendered only if explicitly enabled

### Requirement: Wrestler View empty-state behavior
The system SHALL render an empty-state Wrestler View with a placeholder image and "Select Wrestler", and SHALL render no other blocks while in the empty state.

#### Scenario: Empty-state rendering
- **WHEN** a Wrestler View has no assigned wrestler
- **THEN** only the placeholder image and "Select Wrestler" are shown

### Requirement: Wrestler View avatar rendering
The system SHALL render wrestler avatars using a rich-pixels half renderer from 48x48 PNG assets, defaulting to a standard wrestler image when `avatar_path` is empty or invalid, and MUST NOT crash on image load errors.

#### Scenario: Avatar fallback
- **WHEN** a wrestler has an empty or invalid `avatar_path`
- **THEN** the default wrestler image is rendered without error

### Requirement: Wrestler selection inspection modal
The system SHALL provide a read-only Wrestler View inspection modal from the wrestler selection table, opened with `i` and closed with `Esc`, and SHALL restore focus to the same table row after closing.

#### Scenario: Inspect modal flow
- **WHEN** the user presses `i` on the wrestler selection screen
- **THEN** the inspection modal opens without changing selection
- **AND THEN** pressing `Esc` closes the modal and returns focus to the same row

### Requirement: Match booking rivalry summary header
The system SHALL display an emoji-only rivalry summary in the Match Booking header by aggregating rivalries across all unordered wrestler pairs and compressing counts using ASCII `xN` (e.g., `💥 x3`). The header MUST NOT wrap, scroll, or overflow.

#### Scenario: Rivalry summary aggregation
- **WHEN** a match has multiple rivalry pairs
- **THEN** the header displays each rivalry emoji with an ASCII count suffix

