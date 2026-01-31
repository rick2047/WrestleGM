## Why

Match categories are core game data but are split between `wrestlegm/models.py` and `wrestlegm/constants.py` and passed around as IDs, which causes repeated lookups and fragile coupling. Making match categories a first-class object clarifies ownership, improves consistency, and aligns the model with other domain objects (including match types).

## What Changes

- Rename `MatchCategoryDefinition` to `MatchCategory` and treat match categories as a primary domain model.
- Hardcode the current three categories in one place (replacing the constants dict/order).
- Update `GameState` and callers to use match category objects/registry rather than scattered ID lookups.
- Update `Match`/`MatchResult` to carry `MatchCategory` objects (older save compatibility is not required).
- Replace `MATCH_CATEGORY_ORDER` by ordering categories via their IDs. For now the hardcoded categories are `singles`, `triple-threat`, and `fatal-4-way`, and the order should be exactly that sequence.

## Capabilities

### New Capabilities
- `match-category-model`: First-class match category and match type modeling with hardcoded registries and object references.

### Modified Capabilities
- None.

## Impact

- Domain modeling: `MatchCategory` becomes the source of truth for category metadata.
- `wrestlegm/constants.py` no longer stores match category definitions.
- `GameState`, UI formatting helpers, and match booking flows will move to category objects/registry lookups.
- Direct updates needed in: `wrestlegm/state.py`, `wrestlegm/ui/formatting.py`, `wrestlegm/ui/screens/match_booking.py`, and `wrestlegm/ui/screens/booking_hub.py`.
