## Why

Match categories are core game data but are split between `wrestlegm/models.py` and `wrestlegm/constants.py` and passed around as IDs, which causes repeated lookups and fragile coupling. Making match categories a first-class object clarifies ownership, improves consistency, and aligns the model with other domain objects (including match types).

## What Changes

- Rename `MatchCategoryDefinition` to `MatchCategory` and treat match categories as a primary domain model.
- Hardcode the current three categories in one place (replacing the constants dict/order).
- Update `GameState` and callers to use match category objects/registry rather than scattered ID lookups.
- Update `Match`/`MatchResult` to carry `MatchCategory` objects (with IDs retained for persistence and selection).
- Update match types to reference `MatchCategory` objects (not IDs), and rename `MatchTypeDefinition` to `MatchType`.
- Hardcode match type definitions in `wrestlegm/models.py`, colocated beneath the `MatchType` class.
- Replace `MATCH_CATEGORY_ORDER` with a stable ordering derived from category IDs.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- None.

## Impact

- Domain modeling: `MatchCategory` becomes the source of truth for category metadata, and `MatchType` references `MatchCategory` objects.
- `wrestlegm/constants.py` no longer stores match category definitions.
- `GameState`, UI formatting helpers, and match booking flows will move to category objects/registry lookups.
- `wrestlegm/data.py` and other JSON-loading paths for match types will be replaced by the hardcoded definitions in `wrestlegm/models.py`.
- Direct updates needed in: `wrestlegm/state.py`, `wrestlegm/ui/formatting.py`, `wrestlegm/ui/screens/match_booking.py`, and `wrestlegm/ui/screens/booking_hub.py`.
