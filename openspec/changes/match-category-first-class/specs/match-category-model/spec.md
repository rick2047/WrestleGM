## ADDED Requirements

### Requirement: Match categories are first-class objects
The system SHALL define a `MatchCategory` object with numeric `id`, `name`, and `size`. The system SHALL hardcode exactly three categories with numeric IDs `1`, `2`, and `3` in a single list.

#### Scenario: Match category list is available
- **WHEN** the game initializes
- **THEN** the list contains `MatchCategory` objects with IDs `1`, `2`, and `3`

### Requirement: Match category ordering is stable
The system SHALL provide a stable ordering of match categories based on numeric IDs: `1`, `2`, `3`.

#### Scenario: UI category options use canonical order
- **WHEN** match category options are rendered
- **THEN** the options appear in the order `1`, `2`, `3`

### Requirement: Matches carry match category objects
The system SHALL store a `MatchCategory` object on `Match` and `MatchResult`. Persistence SHALL serialize numeric category IDs and map them back to `MatchCategory` objects during load or construction. Compatibility with older saves is not required.

#### Scenario: Save/load preserves match category
- **WHEN** a match with category ID `1` is serialized and then deserialized
- **THEN** the restored match references the canonical `MatchCategory` with ID `1`
