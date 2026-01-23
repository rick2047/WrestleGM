# Tasks

- [x] Define UI flow test modules that mirror the UI screen structure and move existing flow tests accordingly.
- [x] Add navigation coverage for every screen (including modals and selection screens) with focused flow tests.
- [x] Update CI to generate a UI snapshot PR comment containing a collapsed table of latest snapshot images.
- [x] Ensure snapshot images are always available by uploading artifacts on success for UI snapshot job.
- [x] Keep core test PR comment unchanged and only enhance the UI snapshot job output.
- [x] Update/extend `.github/scripts/pytest_comment.py` (or add a UI-specific script) to render snapshot tables and error details.
## Validation
- `pytest tests/ui_flows/`
- `pytest tests/test_ui_snapshots.py`
