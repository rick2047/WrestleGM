# ui-testing Specification

## Purpose
TBD - created by archiving change add-ui-testing. Update Purpose after archive.
## Requirements
### Requirement: Textual UI test harness
The system SHALL provide a Textual UI test harness that uses Textual test utilities to drive keyboard-only interactions in a deterministic environment.

#### Scenario: Deterministic UI test setup
- **WHEN** UI tests run
- **THEN** they use a fixed RNG seed of 2047
- **AND THEN** they use a fixed viewport size of 100x30

### Requirement: UI test fixtures
The system SHALL provide dedicated UI test fixtures for roster and match type inputs to ensure deterministic flows and snapshots.

#### Scenario: Fixture-based UI data
- **WHEN** UI tests run
- **THEN** they load roster and match type data from `tests/fixtures/ui/`

### Requirement: UI flow tests
The system SHALL include UI flow tests that validate keyboard-only navigation and state progression across core gameplay screens.

#### Scenario: Flow coverage for core gameplay
- **WHEN** UI flow tests run
- **THEN** they cover at least the following journeys:
  - New Game -> Game Hub
  - Game Hub -> Booking Hub -> Back -> Game Hub
  - Booking Hub -> Match Booking -> Select Wrestler A + B + Type -> Confirm -> Booking Hub
  - Booking Hub -> Run Show (after all slots booked) -> Results -> Continue -> Game Hub
  - Game Hub -> Roster Overview -> Back

### Requirement: UI snapshot tests
The system SHALL generate deterministic SVG snapshots for canonical UI screens and stable end states only using `pytest-textual-snapshot`.

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

### Requirement: Snapshot baseline management
The system SHALL store SVG snapshot baselines in-repo using the `pytest-textual-snapshot` naming conventions.

#### Scenario: Baseline location and naming
- **WHEN** baselines are committed
- **THEN** they live under `tests/snapshots/`
- **AND THEN** filenames are derived from snapshot test function names and stored with the `.raw` extension

### Requirement: Snapshot enforcement
The system SHALL fail tests when snapshot output does not match baselines.

#### Scenario: Snapshot mismatch handling
- **WHEN** a generated snapshot differs from its baseline
- **THEN** the test run fails

