# Change: Default match type and booked wrestler indicators

## Why
Booking flow currently requires manual match type selection each time and gives no visual cue when a wrestler is already booked. Defaulting the match type and showing booked indicators reduces friction and mistakes.

## What Changes
- Default match type to the first entry in `data/match_types.json` when booking a new slot.
- Show a booked indicator (📅) in the WrestlerSelectionScreen list for already-booked wrestlers.
- Use the 🥱 emoji consistently for low-stamina wrestlers wherever the fatigue icon appears.

## Impact
- Affected specs: `specs/ui/spec.md`
- Affected code/docs: `wrestlegm/ui.py`
