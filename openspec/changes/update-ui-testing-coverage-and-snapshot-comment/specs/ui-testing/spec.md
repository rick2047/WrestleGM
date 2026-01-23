## MODIFIED Requirements

### Requirement: UI flow tests
The system SHALL include UI flow tests that validate keyboard-only navigation and state progression across core gameplay screens, and SHALL organize them into modules that reflect the UI screen structure.

#### Scenario: Flow coverage for core gameplay
- **WHEN** UI flow tests run
- **THEN** they cover at least the following journeys:
  - New Game -> Game Hub
  - Game Hub -> Booking Hub -> Back -> Game Hub
  - Booking Hub -> Match Booking -> Select Wrestler A + B + Type -> Confirm -> Booking Hub
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
  - S7 Wrestler Selection (default)
  - S8 Match Type Selection (default)
  - S9 Match Booking Confirmation (modal visible)
  - S10 Show Results (default)
  - S11 Roster Overview (default)
  - S12 Booking Hub (rivalry emojis)
  - S13 Booking Hub (cooldown emojis)
  - S14 Match Booking (rivalry emojis)
  - S15 Save Slot Selection (empty)
  - S16 Save Slot Selection (mixed)
  - S17 Name Save Slot Modal
  - S18 Overwrite Save Slot Modal
