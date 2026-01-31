## Context

Match categories are currently defined as dictionaries and a separate order tuple in `wrestlegm/constants.py`. They are referenced throughout the UI and state logic via `match_category_id` lookups. `MatchCategoryDefinition` exists in `wrestlegm/models.py` but is unused. This splits ownership of core domain data, adds repeated lookups, and makes the model less expressive.

## Goals / Non-Goals

**Goals:**
- Promote match categories to first-class domain objects (`MatchCategory`) and use them directly in `GameState`, `Match`, and `MatchResult`.
- Hardcode the three existing categories in code and remove the constants dict/order.
- Persist full `MatchCategory` object data (id/name/size) in saves; compatibility with older saves is not required.
- Simplify match type availability by removing `allowed_categories` filtering.

**Non-Goals:**
- Changing simulation logic, ratings, or booking rules.
- Introducing new match categories or match types beyond the current set.
- Changing match type definitions beyond removing `allowed_categories`.

## Decisions

- **Rename models:**
  - `MatchCategoryDefinition` → `MatchCategory`.
- **Centralize hardcoded definitions in `wrestlegm/models.py`:**
  - Define the three `MatchCategory` instances directly under the class in a single list.
  - Assign numeric IDs: `1` (Singles), `2` (Triple Threat), `3` (Fatal 4-Way).
- **Ordering:**
  - Remove `MATCH_CATEGORY_ORDER` and sort categories by numeric `id` (1, 2, 3).
- **Object usage:**
  - Update `Match` and `MatchResult` to carry a `MatchCategory` object, not an ID string.
  - Persist full `MatchCategory` object data (id/name/size) without relying on an ID lookup helper.
- **Match type availability:**
  - Remove `allowed_categories` from match type data/fixtures.
  - Match types are available for all categories; no category-based filtering.

## Risks / Trade-offs

- **[Risk] Hardcoding reduces flexibility** → Mitigation: keep the definitions centralized and clearly structured in `wrestlegm/models.py` to make future changes straightforward.
- **[Risk] Object identity mismatches** (if categories are re-instantiated) → Mitigation: keep a single in-memory list of `MatchCategory` objects as the source of truth.
- **[Risk] Older saves may fail to load** → Mitigation: accept the break for this change and keep the current save version handling simple.

## Migration Plan

- Introduce `MatchCategory` rename in `wrestlegm/models.py` and define the hardcoded list under the class.
- Update `WrestleGMApp`, `SessionManager`, and `GameState` to use the hardcoded list instead of constants.
- Update all call sites that referenced `constants.MATCH_CATEGORIES` / `MATCH_CATEGORY_ORDER` to use the new registries.
- Update persistence serialization/deserialization to store full category object data derived from `MatchCategory` objects.
- Remove `MATCH_CATEGORIES` and `MATCH_CATEGORY_ORDER` from `wrestlegm/constants.py`.
- Remove `allowed_categories` handling from match type loading and booking UI filtering.

## Open Questions

- None at this time.
