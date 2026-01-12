# Change: Add promo slots, booking, and simulation

## Why
The current MVP only supports three matches per show. Promos are required to match the PRD for show cards and to add non-match booking choices that still affect ratings and progression.

## What Changes
- Add two promo slots to the show card (Match 1, Promo 1, Match 2, Promo 2, Match 3).
- Add promo booking UI flow (single wrestler) and reuse the existing wrestler selection screen.
- Extend roster data with a `mic_skill` attribute used in promo quality.
- Simulate promo quality, stars, popularity deltas, and stamina recovery.
- Compute show rating as the average of all slot ratings (matches + promos).
- Update booking validation to allow low-stamina wrestlers in promo slots while still blocking duplicates.

## Impact
- Affected specs: `specs/ui/spec.md`, `specs/simulation/spec.md`, `specs/game-loop/spec.md`, `specs/data/spec.md`
- Affected code: UI booking hub, booking screens, simulation engine, show applier, data loaders
