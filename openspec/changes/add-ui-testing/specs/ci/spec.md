## ADDED Requirements
### Requirement: UI test execution order
The system SHALL run UI flow tests before UI snapshot tests and SHALL only run UI snapshots if prior stages pass.

#### Scenario: Gated UI snapshot run
- **WHEN** simulation or UI flow tests fail
- **THEN** UI snapshot tests do not run

#### Scenario: Separate CI jobs with dependencies
- **WHEN** the CI workflow runs
- **THEN** UI snapshot tests are executed in a separate job that depends on successful completion of simulation and UI flow test jobs

### Requirement: Snapshot artifact upload
The system SHALL upload newly generated SVG snapshots as CI artifacts when snapshot tests fail.

#### Scenario: Artifact on snapshot failure
- **WHEN** a UI snapshot test fails
- **THEN** the workflow uploads the generated snapshots for review
