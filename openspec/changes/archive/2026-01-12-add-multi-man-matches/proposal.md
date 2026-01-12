# Change: Add multi-man match support

## Why
Issue #28 requires matches with more than two wrestlers, which currently blocks booking and simulation for triple threat and fatal 4-way formats.

## What Changes
- Extend match type data to declare required wrestler counts (min/max) and add Triple Threat + Fatal 4-Way.
- Update match domain objects to store a list of wrestler IDs and results with one winner plus non-winners.
- Generalize outcome, rating, and stat delta simulation to handle 2–4 wrestlers deterministically.
- Update booking flow to select match type before wrestler selection, render the correct number of wrestler rows, and allow changing match type mid-booking.
- Tighten validation so match size matches selected match type and all booked wrestlers are unique and eligible.
- Add/adjust tests covering multi-man simulation, validation, and UI flows.

## Impact
- Affected specs: `openspec/specs/data/spec.md`, `openspec/specs/simulation/spec.md`, `openspec/specs/ui/spec.md`, `openspec/specs/game-loop/spec.md`
- Affected code: `data/match_types.json`, `wrestlegm/models.py`, `wrestlegm/data.py`, `wrestlegm/sim.py`, `wrestlegm/state.py`, `wrestlegm/ui.py`, tests under `tests/`

## Testing
- Simulation: deterministic outcomes/ratings for 2–4 wrestlers; alignment modifier cases (all heels, all faces, heels > faces, faces > heels); winner/non-winner delta application.
- Validation: block incomplete multi-man matches, duplicate wrestlers, invalid wrestler counts vs match type, and low-stamina match bookings.
- UI flow: Booking Hub → Match Type Selection → Match Booking with correct row counts; wrestler selection fills rows; match type change expands or silently trims rows; confirm only enabled when all rows filled and unique.
- Results: show results formatting for multi-man matches (winner + non-winners) and show rating aggregation unchanged.

## UI Mockups

### Booking Hub (example)
```text
┌──────────────────────────────────────┐
│ WrestleGM                            │
│ Show #12                             │
├──────────────────────────────────────┤
│ ▸ Match 1                            │
│   🙂 Kenny Omega vs 😈 Eddie Kingston │
│                                      │
│   Match 2                            │
│   🙂 Jon Moxley vs 😈 Claudio vs 🙂 PAC│
│                                      │
│   Match 3                            │
│   [ Empty ]                          │
│                                      │
├──────────────────────────────────────┤
│ [ Run Show ] (disabled)              │
│ [ Back ]                             │
└──────────────────────────────────────┘
```

### Match Type Selection
```text
┌──────────────────────────────────────┐
│ Match 2                              │
│                                      │
├──────────────────────────────────────┤
│ ▸ Singles                            │
│   Triple Threat                      │
│   Fatal 4-Way                        │
│                                      │
├──────────────────────────────────────┤
│ [ Cancel ]                           │
└──────────────────────────────────────┘
```

### Match Booking (example: Triple Threat)
```text
┌──────────────────────────────────────┐
│ Book Match 2                         │
│ Triple Threat                        │
├──────────────────────────────────────┤
│ ▸ 🙂 Jon Moxley                       │
│                                      │
│   😈 Claudio Castagnoli               │
│                                      │
│   [ Empty ]                          │
│                                      │
│   Match Type                         │
│   Triple Threat                      │
│                                      │
├──────────────────────────────────────┤
│ [ Confirm ] (disabled)               │
│ [ Clear Match ]                      │
│ [ Cancel ]                           │
└──────────────────────────────────────┘
```
