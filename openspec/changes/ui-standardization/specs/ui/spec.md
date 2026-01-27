## ADDED Requirements

### Requirement: Standard screen layout structure
The system SHALL standardize all non-modal UI screens to a `Header → Body → Actions → Footer` structure. The Header SHALL be full-width and display the current screen name centered. The header MAY additionally display compact context outside the centered title, including screen-specific badges (e.g., emoji indicators for match booking) and/or global context derived from game state (e.g., show name/number or currency). The Body region SHALL expand to fill available space and SHALL be implemented as a dedicated layout container with a configurable layout direction; the default Body layout direction SHALL be vertical. The Actions row SHALL be visually and structurally separate from the Body, SHALL contain only `Button` widgets, and SHALL remain pinned above the Footer.

#### Scenario: Header shows current screen name
- **WHEN** any non-modal screen is shown
- **THEN** the header displays the current screen name centered

#### Scenario: Screen-specific header badges
- **WHEN** a non-modal screen defines header context badges
- **THEN** the header displays those badges alongside the screen name
- **AND THEN** the badges update as the underlying screen state changes

#### Scenario: Header can show compact game-state context
- **WHEN** a non-modal screen defines compact header context derived from game state
- **THEN** the header displays that context without shifting the centered screen name

#### Scenario: Match booking header badges
- **WHEN** the match booking screen is shown
- **THEN** the header includes the rivalry and cooldown emoji indicators relevant to the current draft selections
- **AND THEN** the header updates as the draft selections change

#### Scenario: Body expands to fill available space
- **WHEN** any non-modal screen is shown
- **THEN** the body region expands to fill remaining available height between header and actions/footer

#### Scenario: Default vertical body layout
- **WHEN** any non-modal screen is shown
- **THEN** the body container uses a vertical layout direction by default

#### Scenario: Actions are pinned and separate
- **WHEN** a non-modal screen provides action controls
- **THEN** the action buttons are rendered in a dedicated actions row separate from the scrollable body region
- **AND THEN** the actions row remains pinned above the footer

#### Scenario: Modals remain content-sized overlays
- **WHEN** a modal screen is open
- **THEN** it overlays the current screen and sizes to its content
- **AND THEN** it does not render the standard screen header or actions row

### Requirement: Header content per screen
The system SHALL render the following header content on non-modal screens:

| Screen | Header title | Header badges / context |
| ------ | ------------ | ----------------------- |
| Main Menu | `Main Menu` | None |
| Save Slots (new) | `New Game` | None |
| Save Slots (load) | `Load Game` | None |
| Game Hub | `Game Hub` | None |
| Booking Hub | `Booking Hub` | None |
| Match Booking | `Match {N}` | Aggregated rivalry + cooldown emojis for the current draft selection |
| Promo Booking | `Promo {N}` | None |
| Wrestler Selection | Contextual selection title passed by the parent screen | None |
| Roster | `Roster Overview` | None |
| Results | `Show Results` | None |
| Simulating | `Simulating` | None |
| Guard Screen | `Viewport Guard` | None |

Unless explicitly specified above, the header SHALL display no additional badges or game-state context.

#### Scenario: Main menu header title
- **WHEN** the Main Menu screen is shown
- **THEN** the header title is `Main Menu`

#### Scenario: Save slots header title matches mode
- **WHEN** the save slot selection screen is shown in new-game mode
- **THEN** the header title is `New Game`
- **WHEN** the save slot selection screen is shown in load-game mode
- **THEN** the header title is `Load Game`

#### Scenario: Booking hub header title
- **WHEN** the Booking Hub screen is shown
- **THEN** the header title is `Booking Hub`

#### Scenario: Match booking header includes rivalry and cooldown emojis
- **WHEN** the Match Booking screen is shown
- **THEN** the header title follows `Match {N}` for the edited slot
- **AND THEN** the header includes the aggregated rivalry and cooldown emojis for the current draft selection

#### Scenario: Wrestler selection header uses contextual title
- **WHEN** the wrestler selection screen is shown
- **THEN** the header title matches the contextual title provided by the parent screen
