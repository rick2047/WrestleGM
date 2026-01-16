# data Specification

## Purpose
TBD - created by archiving change add-wrestlegm-mvp. Update Purpose after archive.
## Requirements
### Requirement: Data-driven wrestler definitions
The system SHALL load wrestler definitions from `data/wrestlers.json` with fields `id`, `name`, `alignment`, `popularity`, `stamina`, and `mic_skill`.

#### Scenario: Load roster on startup
- **WHEN** the app starts
- **THEN** it loads all wrestler definitions from `data/wrestlers.json`

### Requirement: Optional wrestler fields
The system SHALL not require optional wrestler fields such as `style`, `tags`, or `injury_status`, and SHALL ignore additional fields not used by the MVP.

#### Scenario: Optional wrestler fields ignored
- **WHEN** wrestler data includes extra fields
- **THEN** the app loads the required fields and ignores the extras

### Requirement: Data-driven match type definitions
The system SHALL load match type definitions from `data/match_types.json` with fields `id`, `name`, `description`, `modifiers`, and optional `allowed_categories`. If `allowed_categories` is omitted, the system SHALL treat the match type as available for all categories.

#### Scenario: Load match types on startup
- **WHEN** the app starts
- **THEN** it loads match type definitions including `allowed_categories`
- **AND THEN** match types missing `allowed_categories` are treated as available for all categories
- **AND THEN** the match types include Standard plus Ambulance, and Ambulance is restricted to Singles

#### Scenario: Match type modifier fields
- **WHEN** match type definitions are loaded
- **THEN** modifiers include outcome_chaos, rating_bonus, rating_variance, stamina_cost_winner, stamina_cost_loser, popularity_delta_winner, and popularity_delta_loser

### Requirement: Match category registry
The system SHALL define a static match category registry with `id`, `name`, and `size` fields for each category, and SHALL include Singles (2), Triple Threat (3), and Fatal 4-Way (4).

#### Scenario: Load match categories
- **WHEN** the app starts
- **THEN** the match category registry includes Singles, Triple Threat, and Fatal 4-Way with the correct sizes
