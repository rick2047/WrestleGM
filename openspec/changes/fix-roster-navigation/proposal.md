# Change: Restore roster screen arrow-key navigation

## Why
The roster viewer's Back button is not reachable via arrow-key navigation, which breaks the keyboard-only navigation principles used across the UI.

## What Changes
- Add arrow-key focus cycling between the roster list and Back button.
- Preserve Enter to activate focused widgets and Escape to go back.

## Impact
- Affected specs: `specs/ui/spec.md`
- Affected code/docs: `wrestlegm/ui.py`
