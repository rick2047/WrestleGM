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
The system SHALL store a `MatchCategory` object on `Match` and `MatchResult`. Persistence SHALL serialize the full `MatchCategory` object data (`id`, `name`, `size`) and load it back into `Match`/`MatchResult` without an ID lookup helper. Compatibility with older saves is not required.

#### Scenario: Save/load preserves match category
- **WHEN** a match with category ID `1` is serialized and then deserialized
- **THEN** the restored match has a `MatchCategory` object with `id=1`, `name="Singles"`, and `size=2`

### Requirement: Match types are available for all categories
The system SHALL treat match types as available for all categories and SHALL NOT filter by `allowed_categories`.

#### Scenario: Match type options are unfiltered
- **WHEN** match type options are rendered in the match booking UI
- **THEN** all match types are available regardless of match category
