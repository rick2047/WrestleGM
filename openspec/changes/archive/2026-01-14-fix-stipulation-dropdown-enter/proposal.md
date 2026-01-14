# Change: Fix stipulation dropdown Enter handling

## Why
Pressing Enter on the stipulation dropdown throws an AttributeError due to an invalid super() call, blocking match booking.

## What Changes
- Ensure Enter opens the stipulation dropdown without throwing.
- Preserve Up/Down focus navigation when the dropdown is closed.
- Add coverage for Enter-to-open behavior.

## Impact
- Affected specs: `specs/ui/spec.md`, `specs/ui-testing/spec.md`
- Affected code: `wrestlegm/ui.py`, UI flow tests
