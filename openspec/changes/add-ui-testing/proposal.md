# Change: Add UI testing for Textual screens

## Why
UI regressions are easy to introduce during refactors, and the current test suite only covers simulation logic. Issue #18 calls for Textual-based UI testing to validate core flows and layout stability.

## What Changes
- Add Textual UI flow tests that drive keyboard-only navigation through core game flows.
- Add deterministic SVG snapshot tests for canonical screens and stable states.
- Store snapshot baselines in-repo and fail tests on mismatches.
- Use a fixed RNG seed (2047), fixed viewport size, and dedicated UI test fixtures for roster and match types.
- Update CI workflow expectations to run UI flow tests before UI snapshot tests and upload failing snapshots as artifacts.

## Impact
- Affected specs: `ui-testing`, `ci`
- Affected code: `tests/`, `wrestlegm/ui.py` test harness usage, `.github/workflows/` (PR tests)
