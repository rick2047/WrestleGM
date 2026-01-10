## ADDED Requirements
### Requirement: Data-driven wrestler definitions
The system SHALL load wrestler definitions from `data/wrestlers.json` with fields `id`, `name`, `alignment`, `popularity`, and `stamina`.

#### Scenario: Load roster on startup
- **WHEN** the app starts
- **THEN** it loads all wrestler definitions from `data/wrestlers.json`

### Requirement: Data-driven match type definitions
The system SHALL load match type definitions from `data/match_types.json` with fields `id`, `name`, `description`, and `modifiers`.

#### Scenario: Load match types on startup
- **WHEN** the app starts
- **THEN** it loads all match type definitions from `data/match_types.json`
