# Change: Add Table Formatting to CI PR Comments

## Why
The PR test comment currently lists test results in plain bullet format. Tables per class grouping will make status and reasons easier to scan while keeping the report collapsible.

## What Changes
- Render a table per class grouping in the PR test comment.
- Keep emoji status indicators and per-test reason summaries.
- Preserve collapsible group sections.

## Impact
- Affected specs: `specs/ci/spec.md`
- Affected code/docs: `.github/scripts/pytest_comment.py`
