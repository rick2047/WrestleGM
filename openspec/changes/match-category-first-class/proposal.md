## Why

Match categories are core game data but are split between `wrestlegm/models.py` and `wrestlegm/constants.py` and passed around as IDs, which causes repeated lookups and fragile coupling. Making match categories a first-class object clarifies ownership, improves consistency, and aligns the model with other domain objects.

## What Changes

- Define match categories as `MatchCategory` objects and treat them as a primary domain model.
- Hardcode the current three categories in one place (replacing the constants dict/order).
- Update `GameState` and callers to use match category objects/registry rather than scattered ID lookups.
- Retain category IDs for persistence and selection, but centralize them in the category definitions.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- None.

## Impact

- Domain modeling: `MatchCategoryDefinition` becomes the source of truth for category metadata.
- `wrestlegm/constants.py` no longer stores match category definitions.
- `GameState`, UI formatting helpers, and match booking flows will move to category objects/registry lookups.
