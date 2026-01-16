## MODIFIED Requirements
### Requirement: Save payload and versioning
Save files SHALL be JSON, human-readable, and include a mandatory `version` field. The system SHALL support loading `version = 1` and `version = 2` payloads; saving SHALL write `version = 2`. Loading a higher version SHALL be blocked. Save payloads SHALL include the full game state required to resume planning the next show, including roster stats, current show index, current card state, and the RNG seed. If a `saved_at` field is present, it SHALL be metadata-only and MUST NOT influence simulation.

#### Scenario: Unsupported version blocks load
- **WHEN** a player attempts to load a save with `version` greater than 2
- **THEN** loading is blocked with an error

#### Scenario: Corrupt save payload blocks load
- **WHEN** a save file contains invalid JSON
- **THEN** loading is blocked with an error

#### Scenario: Save includes RNG seed
- **WHEN** a save is created
- **THEN** the RNG seed is persisted alongside the other game state fields

#### Scenario: Load supports version 1 and version 2
- **WHEN** a player loads a save with `version` equal to 1 or 2
- **THEN** the system restores the full game state at a clean show boundary

#### Scenario: Saves write version 2
- **WHEN** a save is created
- **THEN** the payload `version` field is set to 2
