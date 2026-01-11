# Change: Persist roster per session and fix roster refresh

## Why
The roster should be generated once at game start and remain stable for the session. Returning to the roster screen currently raises a `DuplicateIds` exception because existing rows are remounted instead of clearing the view and rebuilding from the persistent state.

## What Changes
- Treat the roster as a persistent session asset (generated once at game start).
- Rebuild the roster list view from `GameState` on resume after clearing existing rows.
- Avoid reusing mounted list item IDs.

## Impact
- Affected specs: `specs/ui/spec.md`
- Affected code/docs: `wrestlegm/ui.py`
