## MODIFIED Requirements
### Requirement: Data-driven match type definitions
The system SHALL load match type definitions from `data/match_types.json` with fields `id`, `name`, `description`, `modifiers`, and optional `allowed_categories`. If `allowed_categories` is omitted, the system SHALL treat the match type as available for all categories.

#### Scenario: Load match types on startup
- **WHEN** the app starts
- **THEN** it loads match type definitions including `allowed_categories`
- **AND THEN** match types missing `allowed_categories` are treated as available for all categories
- **AND THEN** the match types include Standard plus Ambulance, and Ambulance is restricted to Singles
