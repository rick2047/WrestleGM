## ADDED Requirements

### Requirement: Match categories are first-class objects
The system SHALL define a `MatchCategory` object with `id`, `name`, and `size`. The system SHALL hardcode exactly three categories with IDs `singles`, `triple-threat`, and `fatal-4-way` in a canonical registry.

#### Scenario: Match category registry is available
- **WHEN** the game initializes
- **THEN** the canonical registry contains `MatchCategory` objects for `singles`, `triple-threat`, and `fatal-4-way`

### Requirement: Match category ordering is stable
The system SHALL provide a stable ordering of match categories based on the canonical registry order: `singles`, `triple-threat`, `fatal-4-way`.

#### Scenario: UI category options use canonical order
- **WHEN** match category options are rendered
- **THEN** the options appear in the order `singles`, `triple-threat`, `fatal-4-way`

### Requirement: Match types reference match categories
The system SHALL define `MatchType` objects that reference `MatchCategory` objects in `allowed_categories`. Match types SHALL be hardcoded in `wrestlegm/models.py` and use the canonical `MatchCategory` instances.

#### Scenario: Allowed categories use MatchCategory objects
- **WHEN** a match type is validated against a selected category
- **THEN** the validation uses `MatchCategory` objects from the canonical registry

### Requirement: Matches carry match category objects
The system SHALL store a `MatchCategory` object on `Match` and `MatchResult`. Persistence SHALL serialize category IDs and map them back to the canonical `MatchCategory` objects during load or construction.

#### Scenario: Save/load preserves match category
- **WHEN** a match with category ID `singles` is serialized and then deserialized
- **THEN** the restored match references the canonical `MatchCategory` with ID `singles`
