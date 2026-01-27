## Why

The UI currently varies between screens and often doesn’t use the available viewport, which makes the experience feel inconsistent. Standardizing layout will make WrestleGM feel like a cohesive product.

## What Changes

- Add a consistent, full-width header on every non-modal screen that displays the current screen name centered.
- Standardize all non-modal screens to a `header → content → footer` structure, with the content region expanding to fill available height.
- Update global Textual CSS and screen compositions so primary content widgets use the expanded region (scrolling where appropriate).
- Preserve modal behavior as overlay dialogs that size to their content (no modal header, no forced full-height modals).

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `ui`: Require a consistent screen layout (centered header + expanding content + footer) across all non-modal screens, while keeping modals as content-sized overlays.

## Impact

- UI styling: `wrestlegm/ui/styles.tcss`.
- UI screens: `wrestlegm/ui/screens/*` (composition and titles).
- UI docs and tests: `docs/ui.md` and snapshot baselines under `tests/snapshots/test_ui_snapshots/` (expected updates after layout changes).
