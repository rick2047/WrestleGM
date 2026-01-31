## 1. Model and Registry Updates

- [ ] 1.1 Rename `MatchCategoryDefinition` to `MatchCategory` and add a canonical registry of the three hardcoded categories in `wrestlegm/models.py`.
- [ ] 1.2 Rename `MatchTypeDefinition` to `MatchType` and hardcode match type definitions in `wrestlegm/models.py`, referencing `MatchCategory` objects in `allowed_categories`.
- [ ] 1.3 Remove `MATCH_CATEGORIES` and `MATCH_CATEGORY_ORDER` from `wrestlegm/constants.py`.

## 2. State and Persistence Integration

- [ ] 2.1 Update `Match` and `MatchResult` to store `MatchCategory` objects and adjust constructors/usages accordingly.
- [ ] 2.2 Update persistence serialization/deserialization to store category IDs and map them back to canonical `MatchCategory` objects.
- [ ] 2.3 Update `GameState` initialization and validation to use category objects/registry instead of constants.

## 3. UI and Formatting Updates

- [ ] 3.1 Update `wrestlegm/ui/formatting.py` helpers to use the category registry and return names/sizes via `MatchCategory` objects.
- [ ] 3.2 Update match booking UI (`wrestlegm/ui/screens/match_booking.py`) to use the canonical category list and ordering for options and size checks.
- [ ] 3.3 Update booking hub UI (`wrestlegm/ui/screens/booking_hub.py`) to select the default category from the canonical registry.

## 4. Match Type Loading Cleanup

- [ ] 4.1 Remove JSON match type loading paths (`wrestlegm/data.py`) and update app/session setup to import hardcoded match types from `wrestlegm/models.py`.
- [ ] 4.2 Remove or deprecate unused match type JSON data and update any references accordingly.

## 5. Verification

- [ ] 5.1 Run targeted tests or a quick manual TUI smoke check to confirm match booking and show flow still work with category objects.
