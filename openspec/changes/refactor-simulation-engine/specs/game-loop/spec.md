## MODIFIED Requirements
### Requirement: Show-driven progression loop
The system SHALL support a show-driven loop that books a 3-match card, simulates the show via a `SimulationEngine`, applies deltas via a `ShowApplier`, and advances to the next show.

#### Scenario: Complete a show and advance
- **WHEN** the player runs a fully booked show
- **THEN** the system simulates all matches, applies deltas, and increments the show index

## ADDED Requirements
### Requirement: Show applier responsibilities
The system SHALL apply match deltas and between-show recovery through a dedicated `ShowApplier` owned by game state.

#### Scenario: Apply show results through applier
- **WHEN** a show finishes simulation
- **THEN** the `ShowApplier` applies deltas, recovery, and clamping rules
