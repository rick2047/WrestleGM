## MODIFIED Requirements
### Requirement: Data-driven stipulation definitions
The system SHALL load stipulation definitions from `data/match_types.json` with fields `id`, `name`, `description`, `modifiers`, and optional `allowed_categories`. If `allowed_categories` is omitted, the system SHALL treat the stipulation as available for all categories.

#### Scenario: Load stipulations on startup
- **WHEN** the app starts
- **THEN** it loads stipulation definitions including `allowed_categories`
- **AND THEN** stipulations missing `allowed_categories` are treated as available for all categories
- **AND THEN** the stipulations include Standard plus Ambulance, and Ambulance is restricted to Singles
