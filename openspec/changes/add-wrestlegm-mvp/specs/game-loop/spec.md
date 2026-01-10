## ADDED Requirements
### Requirement: Show-driven progression loop
The system SHALL support a show-driven loop that books a 3-match card, simulates the show, applies deltas, and advances to the next show.

#### Scenario: Complete a show and advance
- **WHEN** the player runs a fully booked show
- **THEN** the system simulates all matches, applies deltas, and increments the show index

### Requirement: Show validation rules
The system SHALL prevent running a show unless it has exactly three valid matches, no duplicate wrestlers, and all wrestlers meet stamina requirements.

#### Scenario: Block invalid show run
- **WHEN** the card is incomplete or contains duplicate wrestlers
- **THEN** the system blocks simulation

### Requirement: Between-show recovery
The system SHALL restore stamina to wrestlers who did not participate in the previous show by a fixed amount and clamp to 0–100.

#### Scenario: Resting wrestler recovers stamina
- **WHEN** a wrestler does not appear on the show
- **THEN** their stamina increases by the recovery amount and is clamped to 0–100
