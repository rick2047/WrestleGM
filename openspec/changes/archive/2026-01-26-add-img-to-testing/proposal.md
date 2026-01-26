## Why

UI flow tests currently use fixtures that may omit images, which misses image-dependent paths. We want a stable, image-complete snapshot of current data without coupling tests to live production data.

## What Changes

- Capture a one-time snapshot of the current production wrestler and match type data (including images) into UI test fixtures.
- Update UI flow tests to select wrestlers with image attachments from that snapshot data.
- Keep production and test data separate to avoid test drift from future production updates.
- Seed rivalry data in the UI fixtures so rivalry views are populated without extra test logic.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `ui-testing`: UI test fixtures are derived from a snapshot of current production data and UI flow tests use wrestlers with attached images.

## Impact

- Test fixtures under `tests/fixtures/ui/` and related UI flow tests.
- One-time snapshot workflow from `data/` into fixtures; production data remains separate.
- Potential snapshot baselines and CI expectations if image rendering affects outputs.
