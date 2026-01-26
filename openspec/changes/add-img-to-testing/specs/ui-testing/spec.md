## MODIFIED Requirements

### Requirement: UI test fixtures
The system SHALL provide dedicated UI test fixtures for roster and match type inputs to ensure deterministic flows and snapshots.

#### Scenario: Fixture-based UI data
- **WHEN** UI tests run
- **THEN** they load roster and match type data from `tests/fixtures/ui/`
- **AND THEN** the fixture data is a snapshot of current production data captured intentionally, not a live mirror
- **AND THEN** the snapshot is curated to include image-bearing wrestlers so existing tests exercise image rendering paths without extra selection logic

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

#### Scenario: Image-bearing wrestler coverage via fixtures
- **WHEN** UI flow tests select wrestlers for booking flows
- **THEN** the fixture snapshot ensures the selected wrestlers have image attachments
