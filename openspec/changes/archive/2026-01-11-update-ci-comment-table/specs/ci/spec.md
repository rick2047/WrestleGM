## MODIFIED Requirements
### Requirement: Detailed test listing
The system SHALL include a detailed list of collected tests in the PR comment, grouped by test class, with emoji-only status indicators per test and reasons for skipped or error cases. Each group SHALL render as a table inside a collapsible section. The emoji mapping SHALL be `✅` for passed, `❌` for failed, `🛑` for error, and `⚠️` for skipped.

#### Scenario: Report test details
- **WHEN** the PR test workflow completes
- **THEN** the PR comment lists test cases grouped by class with per-test status and skip/error reasons in a table

## ADDED Requirements
### Requirement: PR test path filters
The system SHALL run PR tests only when relevant files change: `tests/**`, `wrestlegm/**`, `data/**`, `main.py`, `pyproject.toml`, `uv.lock`, or `.github/workflows/pr-tests.yml`.

#### Scenario: Skip PR tests on unrelated changes
- **WHEN** a pull request changes files outside the relevant paths
- **THEN** the PR test workflow does not run
