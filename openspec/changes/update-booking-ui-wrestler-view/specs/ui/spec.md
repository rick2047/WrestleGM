## ADDED Requirements
### Requirement: Minimum viewport guard screen
The system SHALL enforce a minimum terminal viewport of 70 columns by 40 rows at startup. If the terminal is smaller than 70x40 at startup, the system SHALL replace the normal UI with a non-interactive guard screen that only allows quitting the application.

#### Scenario: Guard screen shown on small viewport
- **WHEN** the app starts in a terminal smaller than 70x40
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

## MODIFIED Requirements
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

### Requirement: MVP screen list
The system SHALL provide the MVP screens defined in the PRD, including the startup guard screen for insufficient viewport size.

#### Scenario: MVP screens are available
- **WHEN** the app is running at or above the minimum viewport
- **THEN** the main menu, game hub, booking hub, match booking, promo booking, wrestler selection, results, and roster screens are available

#### Scenario: Guard screen availability
- **WHEN** the app is started in a terminal smaller than 70x40
- **THEN** the guard screen is shown in place of the normal UI

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
│ Wrestlers: [ 2 ▾ ]    Stip: [ Singles ▾ ]     │
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
│   Terminal size too small (need 70x40).       │
│   Resize your terminal and restart the app.  │
│                                              │
│                [ Q ] Quit                    │
│                                              │
└──────────────────────────────────────────────┘
```

## REMOVED Requirements
### Requirement: Match category selection screen
**Reason**: Wrestler count is now selected inline within Match Booking.
**Migration**: Remove the match category selection screen and open Match Booking directly from the booking hub.
