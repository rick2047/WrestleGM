## 1. Model and Registry Updates

- [ ] 1.1 Rename `MatchCategoryDefinition` to `MatchCategory` and add a hardcoded list of the three categories in `wrestlegm/models.py`.
- [ ] 1.2 Remove `MATCH_CATEGORIES` and `MATCH_CATEGORY_ORDER` from `wrestlegm/constants.py`.

## 2. State and Persistence Integration

- [ ] 2.1 Update `Match` and `MatchResult` to store `MatchCategory` objects and adjust constructors/usages accordingly.
- [ ] 2.2 Update persistence serialization/deserialization to store category IDs and map them back to `MatchCategory` objects.
- [ ] 2.3 Update `GameState` initialization and validation to use category objects/list instead of constants.

## 3. UI and Formatting Updates

- [ ] 3.1 Update `wrestlegm/ui/formatting.py` helpers to use the category list and return names/sizes via `MatchCategory` objects.
- [ ] 3.2 Update match booking UI (`wrestlegm/ui/screens/match_booking.py`) to use the category list and ordering for options and size checks.
- [ ] 3.3 Update booking hub UI (`wrestlegm/ui/screens/booking_hub.py`) to select the default category from the category list.

## 4. Verification

- [ ] 4.1 Run targeted tests or a quick manual TUI smoke check to confirm match booking and show flow still work with category objects.
