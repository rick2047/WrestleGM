## ADDED Requirements
### Requirement: Wrestler View component
The system SHALL provide a Wrestler View component built from optional blocks: Avatar, Name+Alignment, Description, Stats, and Rivalry. The component SHALL render only the blocks explicitly enabled by its configuration. In an empty state (no wrestler assigned), the component SHALL render only the placeholder avatar and the Select Wrestler label, and SHALL omit all other blocks.

#### Scenario: Empty Wrestler View omits non-avatar blocks
- **WHEN** a Wrestler View has no assigned wrestler
- **THEN** only the placeholder avatar and Select Wrestler label render
- **AND THEN** the name, stats, description, and rivalry blocks do not render

#### Scenario: Description renders only when present
- **WHEN** a Wrestler View has a non-empty description
- **THEN** the description line renders as-is
- **AND WHEN** the description is empty
- **THEN** the description line is omitted

#### Scenario: Rivalry block variants
- **WHEN** Wrestler View is used in Match Booking
- **THEN** rivalry renders as compact emoji-only badges without scrolling
- **WHEN** Wrestler View is used in inspection contexts
- **THEN** rivalry renders as a full emoji-only list and MAY be scrollable

### Requirement: Wrestler View contexts
The system SHALL provide preset Wrestler View configurations per context.

#### Scenario: Match Booking preset
- **WHEN** Wrestler View is used in Match Booking
- **THEN** Avatar, Name+Alignment, and Stats are enabled
- **AND THEN** Description is disabled
- **AND THEN** Rivalry is enabled in compact mode

#### Scenario: Promo Booking preset
- **WHEN** Wrestler View is used in Promo Booking
- **THEN** Avatar, Name+Alignment, and Stats are enabled
- **AND THEN** Description and Rivalry are disabled

#### Scenario: Selection and inspection presets
- **WHEN** Wrestler View is used in selection inspection contexts
- **THEN** Avatar, Name+Alignment, and Stats are enabled
- **AND THEN** Description is optional and omitted if empty
- **AND THEN** Rivalry is enabled in full-list mode

### Requirement: Match booking rivalry summary header
The Match Booking header SHALL display an emoji-only rivalry intensity summary aggregated across all unordered wrestler pairs using `itertools.combinations(participants, 2)`. Rivalry counts SHALL be compressed with ASCII `xN` suffixes (for example, `💥 x3`). The header SHALL not wrap, scroll, or overflow.

#### Scenario: Aggregated rivalry summary
- **WHEN** the match booking screen has multiple wrestlers selected
- **THEN** the header aggregates rivalries across all unordered wrestler pairs
- **AND THEN** each emoji is rendered with ASCII `xN` compression
- **AND THEN** no wrestler names or pair identifiers appear

#### Scenario: Header layout stability
- **WHEN** the match booking header is rendered
- **THEN** the header does not wrap, scroll, or overflow

### Requirement: Wrestler selection inspection modal
The system SHALL allow opening a read-only Wrestler View modal from the Wrestler Selection screen using the `i` key. The modal SHALL preserve the current table selection and close on Escape, restoring focus to the same row.

#### Scenario: Open and close inspection modal
- **WHEN** the user presses `i` on the Wrestler Selection screen
- **THEN** a Wrestler View modal opens for the highlighted wrestler
- **AND WHEN** the user presses Escape
- **THEN** the modal closes and focus returns to the same table row

## MODIFIED Requirements
### Requirement: Match booking flow
The system SHALL edit matches in a dedicated booking screen, require confirmation before committing, and allow selecting wrestler count inline. The booking screen SHALL render one Wrestler View per required slot based on the selected wrestler count, allow changing match type via an inline dropdown, default the match type to the first available option when booking an empty slot, mark already-booked wrestlers with a 📅 indicator in the selection list, show popularity and stamina in the selection table, display alignment via emoji (Face 😃, Heel 😈), truncate names longer than 18 characters to 15 + `...`, format rows as `{emoji} {name:<18} {sta:>3} {mic:>3} {pop:>3}{fatigue}{booked_marker}`, and use 🥱 consistently for low-stamina indicators.

#### Scenario: Match booking opens without category selection
- **WHEN** the player selects a match slot
- **THEN** match booking opens directly without a match category selection screen

#### Scenario: Inline wrestler count selection
- **WHEN** the player changes the wrestler count in match booking
- **THEN** the screen adds or removes Wrestler View slots to match the count

#### Scenario: Re-selecting wrestler count keeps early picks
- **WHEN** the player reduces the wrestler count
- **THEN** the earliest selected wrestlers remain assigned and extra slots are cleared

#### Scenario: Re-selecting wrestler count adds new slots
- **WHEN** the player increases the wrestler count
- **THEN** existing selected wrestlers remain assigned and new empty slots are added

#### Scenario: Confirm disabled until valid
- **WHEN** the match booking screen has incomplete or invalid selections
- **THEN** the Confirm action is disabled

#### Scenario: Clear Slot availability
- **WHEN** the match slot is empty
- **THEN** Clear Slot is disabled

#### Scenario: Cancel returns to booking hub
- **WHEN** the player selects Cancel or presses Escape in match booking
- **THEN** they return to the booking hub without committing changes

#### Scenario: Draft selections show booked marker
- **WHEN** the wrestler selection screen is opened during match booking
- **THEN** wrestlers already selected in the current draft show a 📅 marker

#### Scenario: Clear Slot returns to booking hub
- **WHEN** the player clears a booked match slot
- **THEN** the slot is emptied and the booking hub is shown

#### Scenario: Default match type for empty slots
- **WHEN** the player books an empty match slot
- **THEN** the match type defaults to the first available option

### Requirement: Promo booking flow
The system SHALL provide a promo booking screen that edits a single wrestler for a promo slot using a Wrestler View and requires confirmation before committing.

#### Scenario: Empty promo slot booking
- **WHEN** the user opens promo booking for an empty slot
- **THEN** the screen shows a single Wrestler View and a disabled Confirm action

#### Scenario: Promo wrestler field opens selection
- **WHEN** the player activates the Wrestler View in promo booking
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
The system SHALL reuse the wrestler selection screen for promo booking and may change only the contextual title text and validation rules needed to allow low-stamina promo selection.

#### Scenario: Promo wrestler selection layout
- **WHEN** the user opens wrestler selection from promo booking
- **THEN** the table layout, columns, and indicators match the match-booking selection screen
- **AND THEN** the inspection modal is available via `i`

### Requirement: Wrestler selection screen layout
The system SHALL render a wrestler selection table with Name/Sta/Mic/Pop columns, an inline message row for blocking errors, Select/Cancel actions, and an inspection modal.

#### Scenario: Wrestler selection components
- **WHEN** the wrestler selection screen renders
- **THEN** it shows the table, inline message row, Select/Cancel actions, and the `i` binding for inspection

### Requirement: Rivalry and cooldown emoji display
The system SHALL display rivalry and cooldown emojis on the match name line in the Booking Hub and SHALL display the rivalry summary header on the Match Booking screen, updating the summary as wrestlers are added or removed.

#### Scenario: Booking hub emojis
- **WHEN** a match slot is rendered in the Booking Hub
- **THEN** rivalry and cooldown emojis appear on the same line as the match name

#### Scenario: Match booking summary header
- **WHEN** the match booking screen has at least two wrestlers selected
- **THEN** the header shows the aggregated rivalry summary and updates as selections change

### Requirement: Rivalry and cooldown emoji mapping and order
The system SHALL map rivalry levels to ⚡, 🔥, ⚔️, and 💥 for levels 1-4 respectively, and SHALL map cooldown remaining shows to 🧊 (6-5), ❄️ (4-3), and 💧 (2-1). Booking Hub emoji order SHALL follow the unique pair order derived from the booked wrestler list. The Match Booking summary SHALL aggregate counts and SHALL NOT reflect pair order.

#### Scenario: Emoji mapping and ordering
- **WHEN** a match includes multiple rivalry or cooldown pairs in the Booking Hub
- **THEN** emojis are ordered by the unique pair order derived from the match wrestler list
- **AND THEN** each emoji uses the correct mapping for the pair's rivalry level or cooldown remaining shows

### Requirement: MVP screen list
The system SHALL provide the following MVP screens: Main Menu, Save Slot Selection, Game Hub, Booking Hub, Match Booking, Promo Booking, Wrestler Selection, Match Confirmation modal, Simulating Show, Show Results, Name Save Slot modal, Overwrite Save Slot modal, and Roster Overview.

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

### Requirement: Widget mapping
The system SHALL map each screen to the following primary Textual widgets.

| Screen               | Primary Widgets             |
| -------------------- | --------------------------- |
| Main Menu            | ListView, Static, Footer    |
| Game Hub             | ListView, Static, Footer    |
| Booking Hub          | ListView, Static, Button    |
| Match Booking        | ListView, Select, Static, Button |
| Promo Booking        | ListView, Static, Button    |
| Wrestler Selection   | DataTable, Static, Button, ModalScreen |
| Match Booking Confirmation | ModalScreen, Static, Button |
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

#### Match Booking
```
┌──────────────────────────────────────────────┐
│ Match #1        💥 x3  ⚔️ x1                  │
├──────────────────────────────────────────────┤
│ Wrestlers: [ 3 ▾ ]    Type: [ ▾ ]             │
│                                              │
│ Wrestlers (VerticalScroll)                    │
│  ▶ ┌───────────────┐ 😃 Kazuchika Okada       │
│    │ avatar.png    │ ⭐92  🔋28  🎤88          │
│    │ (half render) │ 💥 ⚔️ 🔥                 │
│    └───────────────┘                          │
│                                              │
│    ┌───────────────┐ 😈 Jay White             │
│    │ avatar.png    │ ⭐85  🔋40  🎤70          │
│    │ (half render) │ 💥 🔥                    │
│    └───────────────┘                          │
│                                              │
│    ┌───────────────┐ Select Wrestler          │
│    │ placeholder   │                          │
│    │ (half render) │                          │
│    └───────────────┘                          │
│                                              │
│ [ Clear Slot ]   [ Confirm ]   [ Back ]       │
└──────────────────────────────────────────────┘
```

#### Promo Booking
```
┌──────────────────────────────────────────────┐
│ Promo Slot #2                                 │
├──────────────────────────────────────────────┤
│ Type: [ Promo ▾ ]                             │
│                                              │
│ Performer                                     │
│  ▶ ┌───────────────┐ Select Wrestler          │
│    │ placeholder   │                          │
│    │ (half render) │                          │
│    └───────────────┘                          │
│                                              │
│ [ Clear Slot ]   [ Confirm ]   [ Back ]       │
└──────────────────────────────────────────────┘
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

#### Wrestler Selection (Inspect Modal Open)
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
│ │ ┌───────────────┐ 😃 Kazuchika Okada     │ │
│ │ │ avatar.png    │ ⭐92  🔋28  🎤88        │ │
│ │ │ (half render) │ "Ace of the Rainmaker…"│ │
│ │ └───────────────┘                          │ │
│ │                                            │ │
│ │ Rivalries                                   │ │
│ │  💥 Kenny Omega                             │ │
│ │  ⚔️ Tetsuya Naito                           │ │
│ │  🔥 Jay White                               │ │
│ │                                            │ │
│ │              [ Esc to close ]               │ │
│ └──────────────────────────────────────────┘ │
└──────────────────────────────────────────────┘
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

## REMOVED Requirements
### Requirement: Match category selection screen
**Reason**: Match booking now selects wrestler count inline, so the category selection screen is removed.
**Migration**: Open match booking directly from the booking hub and update flows/tests accordingly.
