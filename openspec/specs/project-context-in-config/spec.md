# project-context-in-config Specification

## Purpose
TBD - created by archiving change migrate-openspec-context. Update Purpose after archive.
## Requirements
### Requirement: Canonical project context lives in config
The project context MUST be defined under the `context:` field in `openspec/config.yaml` and be sufficient to replace `openspec/project.md`.

#### Scenario: Artifact generation reads config context
- **WHEN** an OpenSpec artifact is generated
- **THEN** the project context comes from `openspec/config.yaml`
- **AND** `openspec/project.md` is not required

### Requirement: Context is comprehensive
The config context MUST include the product vision, gameplay constraints, UI/UX constraints, simulation principles, tech stack, and testing expectations used by the project.

#### Scenario: Context captures key constraints
- **WHEN** a contributor reviews the config context
- **THEN** they can identify the core gameplay loop, UI constraints, determinism requirements, and dependency expectations

