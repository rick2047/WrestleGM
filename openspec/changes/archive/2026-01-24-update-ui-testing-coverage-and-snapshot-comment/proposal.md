# Change: Improve UI test coverage and snapshot reporting

## Why
We need higher confidence that navigation and every screen render correctly, and we need CI to surface the latest UI snapshots in a compact, scannable format.

## What Changes
- Split UI flow tests by screen/flow area to mirror the UI module structure and make navigation coverage explicit.
- Add navigation coverage for all screens to ensure routing works end-to-end.
- Update the UI test PR comment to include a collapsed table of the latest snapshot images (with error details when snapshots fail).
- Limit the snapshot comment enhancement to the UI snapshot job only.

## Impact
- Affected specs: `ui-testing`, `ci`.
- Affected code: UI test layout under `tests/`, CI comment generation in `.github/scripts/pytest_comment.py` and the UI snapshot job in `.github/workflows/pr-tests.yml`.
- UI/UX: no product UI changes.

## Non-Goals
- No changes to simulation logic or game rules.
- No changes to snapshot baselines unless required by new coverage.

## Risks & Mitigations
- Risk: Comment size grows with embedded snapshots.
  Mitigation: use collapsed `<details>` sections and a compact table with thumbnails.
- Risk: Snapshot artifacts missing on success.
  Mitigation: publish artifacts on success for the UI snapshot job (or generate inline images from repo baselines as a fallback).

## UI Mockups
No product UI changes.
