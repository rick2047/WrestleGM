## ADDED Requirements
### Requirement: Viewport guard tests
The system SHALL include UI tests that validate the startup viewport guard behavior for terminals smaller than 70x40.

#### Scenario: Guard screen validation
- **WHEN** the app starts with a viewport smaller than 70x40
- **THEN** the guard screen is shown and only the Quit action is available

## MODIFIED Requirements
### Requirement: Textual UI test harness
The system SHALL provide a Textual UI test harness that uses Textual test utilities to drive keyboard-only interactions in a deterministic environment.

#### Scenario: Deterministic UI test setup
- **WHEN** UI tests run
- **THEN** they use a fixed RNG seed of 2047
- **AND THEN** they use a fixed viewport size of 80x40

### Requirement: UI flow tests
The system SHALL include UI flow tests that validate keyboard-only navigation and state progression across core gameplay screens, and SHALL organize them into modules that reflect the UI screen structure.

#### Scenario: Flow coverage for core gameplay
- **WHEN** UI flow tests run
- **THEN** they cover at least the following journeys:
  - New Game -> Game Hub
  - Game Hub -> Booking Hub -> Back -> Game Hub
  - Booking Hub -> Match Booking -> Select wrestler count -> Select Wrestler A + B + Type -> Confirm -> Booking Hub
  - Booking Hub -> Run Show (after all slots booked) -> Results -> Continue -> Game Hub
  - Game Hub -> Roster Overview -> Back

#### Scenario: Screen-aligned flow modules
- **WHEN** UI flow tests are organized
- **THEN** they are split into modules that mirror `wrestlegm/ui/screens/*` and each screen has at least one navigation flow test

### Requirement: UI snapshot tests
The system SHALL generate deterministic SVG snapshots for canonical UI screens and stable end states only using `pytest-textual-snapshot`, and SHALL publish a stable list of snapshot names for CI reporting.

#### Scenario: Canonical snapshot registry
- **WHEN** snapshot tests run
- **THEN** the snapshot registry is fixed to the following list:
  - S1 Main Menu (default)
  - S2 Game Hub (default)
  - S3 Booking Hub (all slots empty)
  - S4 Booking Hub (all slots filled)
  - S5 Match Booking (empty slot)
  - S6 Match Booking (filled slot)
  - S7 Promo Booking (empty slot)
  - S8 Promo Booking (filled slot)
  - S9 Wrestler Selection (default)
  - S10 Wrestler Selection (inspect modal)
  - S11 Match Booking Confirmation (modal visible)
  - S12 Show Results (default)
  - S13 Roster Overview (default)
  - S14 Booking Hub (rivalry emojis)
  - S15 Booking Hub (cooldown emojis)
  - S16 Match Booking (rivalry summary)
  - S17 Guard Screen (viewport too small)
  - S18 Save Slot Selection (empty)
  - S19 Save Slot Selection (mixed)
  - S20 Name Save Slot Modal
  - S21 Overwrite Save Slot Modal
