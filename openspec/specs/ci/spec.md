# ci Specification

## Purpose
TBD - created by archiving change add-pr-ci. Update Purpose after archive.
## Requirements
### Requirement: PR test workflow
The system SHALL run automated tests via `uv run pytest` for every pull request.

#### Scenario: Pull request test run
- **WHEN** a pull request is opened or updated
- **THEN** the workflow runs `uv run pytest` and reports the outcome

### Requirement: Sticky PR test comment
The system SHALL publish a single sticky PR comment with the latest test outcome and update it on each workflow run.

#### Scenario: Update PR test comment
- **WHEN** the PR test workflow completes
- **THEN** the existing test comment is updated with the new result

### Requirement: Detailed test listing
The system SHALL include a detailed list of collected tests in the PR comment, grouped by test class, with emoji-only status indicators per test and reasons for skipped or error cases. Each group SHALL render as a table inside a collapsible section. The emoji mapping SHALL be `✅` for passed, `❌` for failed, `🛑` for error, and `⚠️` for skipped.

#### Scenario: Report test details
- **WHEN** the PR test workflow completes
- **THEN** the PR comment lists test cases grouped by class with per-test status and skip/error reasons in a table

### Requirement: Workflow permissions
The workflow SHALL request only the permissions needed to read code and update PR comments.

#### Scenario: Minimal token access
- **WHEN** the workflow runs
- **THEN** it uses read access for repository contents and write access for PR comments

### Requirement: PR test path filters
The system SHALL run PR tests only when relevant files change: `tests/**`, `wrestlegm/**`, `data/**`, `main.py`, `pyproject.toml`, `uv.lock`, or `.github/workflows/pr-tests.yml`.

#### Scenario: Skip PR tests on unrelated changes
- **WHEN** a pull request changes files outside the relevant paths
- **THEN** the PR test workflow does not run

