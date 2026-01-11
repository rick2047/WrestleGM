# Change: Restore arrow-key navigation across booking and results screens

## Why
Arrow-key navigation currently gets stuck on list views, so users cannot reach action buttons like Confirm, Back, or Run Show on key-only flows. This blocks core booking and results workflows.

## What Changes
- Ensure arrow keys move focus from list views to action buttons on booking hub, match booking, and results screens.
- Preserve Enter for activate and Escape for back/cancel.
- Keep focus order consistent with the intended flow.

## Impact
- Affected specs: `specs/ui/spec.md`
- Affected code/docs: `wrestlegm/ui.py`
