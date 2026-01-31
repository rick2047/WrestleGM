## ADDED Requirements

### Requirement: Match categories are first-class objects
The system SHALL define a `MatchCategory` object with `id`, `name`, and `size`. The system SHALL hardcode exactly three categories with IDs `singles`, `triple-threat`, and `fatal-4-way` in a single list.

#### Scenario: Match category list is available
- **WHEN** the game initializes
- **THEN** the list contains `MatchCategory` objects for `singles`, `triple-threat`, and `fatal-4-way`

### Requirement: Match category ordering is stable
The system SHALL provide a stable ordering of match categories based on the hardcoded list order: `singles`, `triple-threat`, `fatal-4-way`.

#### Scenario: UI category options use canonical order
- **WHEN** match category options are rendered
- **THEN** the options appear in the order `singles`, `triple-threat`, `fatal-4-way`

### Requirement: Matches carry match category objects
The system SHALL store a `MatchCategory` object on `Match` and `MatchResult`. Persistence SHALL serialize category IDs and map them back to `MatchCategory` objects during load or construction. Compatibility with older saves is not required.

#### Scenario: Save/load preserves match category
- **WHEN** a match with category ID `singles` is serialized and then deserialized
- **THEN** the restored match references the canonical `MatchCategory` with ID `singles`
