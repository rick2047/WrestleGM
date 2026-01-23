## ADDED Requirements

### Requirement: UI snapshot PR comment
The system SHALL publish a UI snapshot PR comment from the UI snapshot job that shows the latest snapshot images in a collapsed table, and SHALL display error details when snapshot generation fails.

#### Scenario: Snapshot table in PR comment
- **WHEN** UI snapshot tests succeed
- **THEN** the PR comment includes a collapsed section with a table of the latest snapshots (one row per screen)

#### Scenario: Snapshot failure reporting
- **WHEN** UI snapshot tests fail
- **THEN** the PR comment includes the failure summary and any available snapshot images, and omits missing images gracefully

### Requirement: Snapshot artifact availability
The system SHALL upload UI snapshot artifacts on both success and failure so the PR comment can reference the latest images.

#### Scenario: Snapshot artifacts on success
- **WHEN** UI snapshot tests succeed
- **THEN** the workflow uploads snapshot artifacts for the latest run
