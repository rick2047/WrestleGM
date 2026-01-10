# Change: Add PR Test Workflow With Sticky Comment

## Why
The project needs automated PR validation and a visible, continuously updated test result summary on each PR.

## What Changes
- Add a GitHub Actions workflow to run `uv run pytest` on pull requests.
- Post a sticky PR comment summarizing the test outcome and update it on reruns.
- Grant the workflow the minimal permissions required to update PR comments.

## Impact
- Affected specs: `specs/ci/spec.md` (new capability)
- Affected code/docs: `.github/workflows/`, `openspec/specs/`
