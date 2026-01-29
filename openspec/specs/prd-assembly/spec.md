# prd-assembly Specification

## Purpose
TBD - created by archiving change migrate-openspec-context. Update Purpose after archive.
## Requirements
### Requirement: PRD references config context
PRD assembly MUST reference the project context stored in `openspec/config.yaml` instead of `openspec/project.md`.

#### Scenario: Assemble the PRD
- **WHEN** `make_prd.sh` assembles the PRD
- **THEN** the resulting PRD includes the config-based context
- **AND** `openspec/project.md` is not referenced

