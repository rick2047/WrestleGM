## MODIFIED Requirements

### Requirement: Data-driven match type definitions
The system SHALL load match type definitions from `data/match_types.json` with fields `id`, `name`, `description`, `modifiers`, `base_cost`, and optional `allowed_categories`. If `allowed_categories` is omitted, the system SHALL treat the match type as available for all categories. If `base_cost` is omitted, the system SHALL default it to 0.

#### Scenario: Load match types on startup
- **WHEN** the app starts
- **THEN** it loads match type definitions including `allowed_categories` and `base_cost`
- **AND THEN** match types missing `allowed_categories` are treated as available for all categories
- **AND THEN** match types missing `base_cost` default to 0
- **AND THEN** the match types include Standard plus Ambulance, and Ambulance is restricted to Singles

#### Scenario: Match type modifier fields
- **WHEN** match type definitions are loaded
- **THEN** modifiers include outcome_chaos, rating_bonus, rating_variance, stamina_cost_winner, stamina_cost_loser, popularity_delta_winner, and popularity_delta_loser
