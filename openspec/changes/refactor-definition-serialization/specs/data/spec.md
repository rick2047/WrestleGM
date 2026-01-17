## MODIFIED Requirements

### Requirement: Data-driven wrestler definitions
The system SHALL load wrestler data from `data/wrestlers.json` with fields `id`, `name`, `alignment`, `popularity`, `stamina`, and `mic_skill`, and SHALL hydrate the core wrestler model via `from_dict` helpers rather than `*Definition` classes.

#### Scenario: Load roster on startup
- **WHEN** the app starts
- **THEN** it loads all wrestler data from `data/wrestlers.json`
- **AND THEN** it constructs core wrestler model instances using `from_dict`

### Requirement: Data-driven match type definitions
The system SHALL load match type data from `data/match_types.json` with fields `id`, `name`, `description`, `modifiers`, and optional `allowed_categories`. If `allowed_categories` is omitted, the system SHALL treat the match type as available for all categories, and SHALL hydrate the core match type model via `from_dict` helpers rather than `*Definition` classes.

#### Scenario: Load match types on startup
- **WHEN** the app starts
- **THEN** it loads match type data including `allowed_categories`
- **AND THEN** match types missing `allowed_categories` are treated as available for all categories
- **AND THEN** the match types include Standard plus Ambulance, and Ambulance is restricted to Singles
- **AND THEN** it constructs core match type model instances using `from_dict`

## ADDED Requirements

### Requirement: Dataclass serialization helpers
The system SHALL provide `from_dict`/`to_dict` helpers on core data model dataclasses to support JSON serialization using standard `dataclasses` utilities.

#### Scenario: Serialize and deserialize data models
- **WHEN** a core data model is serialized or loaded
- **THEN** `to_dict` uses `dataclasses.asdict` and `from_dict` reconstructs nested data structures
