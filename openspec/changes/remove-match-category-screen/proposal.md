# Change: Remove Match Category Selection Screen

## Why
The match category selection screen is no longer part of the booking flow now that wrestler count is selected inline on the match booking screen. Keeping the unused screen and docs/spec references creates confusion and extra maintenance.

## What Changes
- Remove the `MatchCategorySelectionScreen` implementation and exports.
- Update booking flow documentation and UI specs to reflect direct navigation to match booking.
- Align navigation wording and examples to the current routing behavior.
- Verify UI flow tests and utilities remain consistent (update only if needed).

## Impact
- Affected specs: `ui`
- Affected docs: `docs/ui.md`
- Affected code: `wrestlegm/ui/screens/match_category_selection.py`, `wrestlegm/ui/screens/__init__.py`, `wrestlegm/ui/__init__.py`
