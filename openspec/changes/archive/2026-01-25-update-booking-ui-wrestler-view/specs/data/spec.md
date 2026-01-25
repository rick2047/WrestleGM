## MODIFIED Requirements
### Requirement: Data-driven wrestler definitions
The system SHALL load wrestler definitions from `data/wrestlers.json` with fields `id`, `name`, `alignment`, `popularity`, `stamina`, `mic_skill`, `description`, and `avatar_path`. If `description` or `avatar_path` is missing, the system SHALL default it to an empty string.

#### Scenario: Load roster on startup
- **WHEN** the app starts
- **THEN** it loads all wrestler definitions from `data/wrestlers.json` including `description` and `avatar_path`
- **AND THEN** missing `description` or `avatar_path` fields default to empty strings

### Requirement: Optional wrestler fields
The system SHALL ignore optional wrestler fields beyond the defined schema (such as `style`, `tags`, or `injury_status`) while preserving the required fields including `description` and `avatar_path`.

#### Scenario: Optional wrestler fields ignored
- **WHEN** wrestler data includes extra fields
- **THEN** the app loads the required fields and ignores the extras
