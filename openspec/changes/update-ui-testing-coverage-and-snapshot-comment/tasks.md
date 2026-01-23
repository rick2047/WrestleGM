# Tasks

- [ ] Define UI flow test modules that mirror the UI screen structure and move existing flow tests accordingly.
- [ ] Add navigation coverage for every screen (including modals and selection screens) with focused flow tests.
- [ ] Update CI to generate a UI snapshot PR comment containing a collapsed table of latest snapshot images.
- [ ] Ensure snapshot images are always available by uploading artifacts on success for UI snapshot job.
- [ ] Keep core test PR comment unchanged and only enhance the UI snapshot job output.
- [ ] Update/extend `.github/scripts/pytest_comment.py` (or add a UI-specific script) to render snapshot tables and error details.
- [ ] Validate: `pytest tests/ui_flows/` and `pytest tests/test_ui_snapshots.py`.

## Validation
- `pytest tests/ui_flows/`
- `pytest tests/test_ui_snapshots.py`
