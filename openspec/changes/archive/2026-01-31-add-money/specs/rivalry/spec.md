## ADDED Requirements

### Requirement: Rivalry and cooldown counts for demand
The system SHALL provide counts of active rivalry pairs and cooldown pairs present in a booked show card for audience computation.

#### Scenario: Rivalry pair counting
- **WHEN** a booked show card is evaluated
- **THEN** the system returns the count of active rivalry pairs across all matches

#### Scenario: Cooldown pair counting
- **WHEN** a booked show card is evaluated
- **THEN** the system returns the count of cooldown pairs across all matches
