# Match Category Refactor Thoughts

## Goal
Make match categories a first-class object similar to MatchType, while keeping them hardcoded (not JSON loaded).

## Current State
- Match categories are defined in `wrestlegm/constants.py` as dicts plus `MATCH_CATEGORY_ORDER`.
- Most code passes around `match_category_id` strings and looks up category data via constants.
- `MatchCategoryDefinition` exists in `wrestlegm/models.py` but is not used (and should be renamed to `MatchCategory`).

## Proposed Direction (Low Risk, Consistent With Match Types)
1) Create a hardcoded registry for categories.
   - Prefer a new `wrestlegm/match_categories.py` to keep `data.py` focused on JSON loading.
   - Return a list of `MatchCategory` in the desired order.
2) Thread categories through app/session/state.
   - `WrestleGMApp` loads categories and passes them into `SessionManager` and `GameState`.
   - `SessionManager` stores the category defs and uses them for new/load games.
   - `GameState` keeps:
     - `match_categories: dict[str, MatchCategory]`
     - `match_category_order: list[str]` (derived from the list order)
3) Replace constants usage with state or registry usage.
   - `GameState.validate_match` uses `self.match_categories.get(id)` and `category.size`.
   - UI formatting helpers should import from a standalone registry module (not GameState).
   - `match_booking.py` uses registry for max size and options.
   - `booking_hub.py` uses `match_category_order` for default category.
4) Remove `MATCH_CATEGORIES` and `MATCH_CATEGORY_ORDER` from `constants.py`.

5) Move match types out of JSON and into `wrestlegm/match_types.py`.
   - Rename `MatchTypeDefinition` to `MatchType`.
   - `MatchType.allowed_categories` should reference `MatchCategory` objects directly.

## Alternative (More Invasive)
- Store `MatchCategory` directly on `Match` and `MatchResult` instead of IDs.
- This reduces lookups but requires persistence changes and JSON compatibility work.
- Bigger refactor than needed if IDs are acceptable.

## Affected Files (Likely)
- `wrestlegm/constants.py` (remove category dicts)
- `wrestlegm/models.py` (rename MatchCategoryDefinition → MatchCategory, MatchTypeDefinition → MatchType)
- `wrestlegm/match_categories.py`
- `wrestlegm/match_types.py`
- `wrestlegm/ui/app.py`
- `wrestlegm/session.py`
- `wrestlegm/state.py`
- `wrestlegm/ui/formatting.py`
- `wrestlegm/ui/screens/match_booking.py`
- `wrestlegm/ui/screens/booking_hub.py`

## Open Questions
- Is keeping `match_category_id` on Match/MatchResult acceptable for now? (saves are simpler)
