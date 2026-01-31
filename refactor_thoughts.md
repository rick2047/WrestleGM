# Match Category Refactor Thoughts

## Goal
Make match categories a first-class object similar to MatchTypeDefinition, while keeping them hardcoded (not JSON loaded).

## Current State
- Match categories are defined in `wrestlegm/constants.py` as dicts plus `MATCH_CATEGORY_ORDER`.
- Most code passes around `match_category_id` strings and looks up category data via constants.
- `MatchCategoryDefinition` exists in `wrestlegm/models.py` but is not used.

## Proposed Direction (Low Risk, Consistent With Match Types)
1) Create a hardcoded loader or registry for categories.
   - Example: add `load_match_categories()` in `wrestlegm/data.py` (or a new `wrestlegm/match_categories.py`).
   - Return a list of `MatchCategoryDefinition` in the desired order.
2) Thread categories through app/session/state.
   - `WrestleGMApp` loads categories and passes them into `SessionManager` and `GameState`.
   - `SessionManager` stores the category defs and uses them for new/load games.
   - `GameState` keeps:
     - `match_categories: dict[str, MatchCategoryDefinition]`
     - `match_category_order: list[str]` (derived from the list order)
3) Replace constants usage with state or registry usage.
   - `GameState.validate_match` uses `self.match_categories.get(id)` and `category.size`.
   - UI formatting helpers either accept a registry/state or import from a new registry module.
   - `match_booking.py` uses registry for max size and options.
   - `booking_hub.py` uses `match_category_order` for default category.
4) Remove `MATCH_CATEGORIES` and `MATCH_CATEGORY_ORDER` from `constants.py`.

## Alternative (More Invasive)
- Store `MatchCategoryDefinition` directly on `Match` and `MatchResult` instead of IDs.
- This reduces lookups but requires persistence changes and JSON compatibility work.
- Bigger refactor than needed if IDs are acceptable.

## Affected Files (Likely)
- `wrestlegm/constants.py` (remove category dicts)
- `wrestlegm/models.py` (MatchCategoryDefinition already present)
- `wrestlegm/data.py` or new `wrestlegm/match_categories.py`
- `wrestlegm/ui/app.py`
- `wrestlegm/session.py`
- `wrestlegm/state.py`
- `wrestlegm/ui/formatting.py`
- `wrestlegm/ui/screens/match_booking.py`
- `wrestlegm/ui/screens/booking_hub.py`

## Open Questions
- Should formatting helpers depend on GameState, or on a standalone registry module?
- Is keeping `match_category_id` on Match/MatchResult acceptable for now? (saves are simpler)
