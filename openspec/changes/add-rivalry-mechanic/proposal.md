# Change: Add rivalry mechanic

## Why
WrestleGM needs narrative continuity across shows so repeated matchups build stakes and payoff instead of feeling isolated.

## What Changes
- Add deterministic rivalry tracking per wrestler pair with progression, blowoff, and cooldown.
- Apply rivalry and cooldown effects to match ratings (bonuses and penalties).
- Surface rivalry/cooldown state as emojis on match name lines in booking UI.

## Impact
- Affected specs: rivalry (new), simulation, ui
- Affected code: wrestlegm/models.py, wrestlegm/state.py, wrestlegm/sim.py, wrestlegm/ui.py, tests/
- Data model: add pairwise rivalry and cooldown state storage
