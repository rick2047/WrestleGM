## MODIFIED Requirements
### Requirement: Data-driven wrestler definitions
The system SHALL load wrestler definitions from `data/wrestlers.json` with fields `id`, `name`, `alignment`, `popularity`, `stamina`, `mic_skill`, `description`, and `avatar_path`. The `description` and `avatar_path` fields MAY be empty strings but SHALL be present in each definition.

#### Scenario: Load roster on startup
- **WHEN** the app starts
- **THEN** it loads all wrestler definitions from `data/wrestlers.json`
- **AND THEN** each definition includes `description` and `avatar_path` fields

### Requirement: Optional wrestler fields
The system SHALL not require optional wrestler fields such as `style`, `tags`, or `injury_status`, and SHALL ignore additional fields not used by the MVP.

#### Scenario: Optional wrestler fields ignored
- **WHEN** wrestler data includes extra fields
- **THEN** the app loads the required fields and ignores the extras
