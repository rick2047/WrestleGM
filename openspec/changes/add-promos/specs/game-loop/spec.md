## MODIFIED Requirements
### Requirement: Show-driven progression loop
The system SHALL support a show-driven loop that books a 3-match, 2-promo card, simulates the show via a `SimulationEngine`, applies deltas via a `ShowApplier`, and advances to the next show.

#### Scenario: Complete a show and advance
- **WHEN** the player runs a fully booked show
- **THEN** the system simulates all match and promo slots, applies deltas, and increments the show index

### Requirement: Show validation rules
The system SHALL prevent running a show unless it has exactly three valid matches, two promos each with a wrestler assigned, no duplicate wrestlers across any slot, and all match-booked wrestlers meet stamina requirements.

#### Scenario: Block invalid show run
- **WHEN** the card is incomplete, contains duplicate wrestlers, or has a match wrestler below stamina requirements
- **THEN** the system blocks simulation

### Requirement: Between-show recovery
The system SHALL restore stamina to wrestlers who did not participate in the previous show by a fixed amount and clamp to 0–100.

#### Scenario: Resting wrestler recovers stamina
- **WHEN** a wrestler does not appear in any match or promo on the show
- **THEN** their stamina increases by the recovery amount and is clamped to 0–100

### Requirement: Show applier responsibilities
The system SHALL apply match deltas, promo deltas, and between-show recovery through a dedicated `ShowApplier` owned by game state.

#### Scenario: Apply show results through applier
- **WHEN** a show finishes simulation
- **THEN** the `ShowApplier` applies match deltas, promo deltas, recovery, and clamping rules
