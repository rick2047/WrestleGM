## MODIFIED Requirements
### Requirement: Data-driven match type definitions
The system SHALL load match type definitions from `data/match_types.json` with fields `id`, `name`, `description`, `modifiers`, `min_wrestlers`, and `max_wrestlers`. If `min_wrestlers` or `max_wrestlers` are omitted, the system SHALL treat both as 2.

#### Scenario: Load match types on startup
- **WHEN** the app starts
- **THEN** it loads match type definitions including `min_wrestlers` and `max_wrestlers`
- **AND THEN** match types missing `min_wrestlers` or `max_wrestlers` are treated as 2/2
- **AND THEN** the match types include Singles (2/2), Triple Threat (3/3), and Fatal 4-Way (4/4)
