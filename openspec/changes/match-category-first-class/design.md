## Context

Match categories are currently defined as dictionaries and a separate order tuple in `wrestlegm/constants.py`. They are referenced throughout the UI and state logic via `match_category_id` lookups. `MatchCategoryDefinition` exists in `wrestlegm/models.py` but is unused. Match types are loaded from JSON and represented as `MatchTypeDefinition`, with `allowed_categories` expressed as ID strings. This splits ownership of core domain data, adds repeated lookups, and makes the model less expressive.

## Goals / Non-Goals

**Goals:**
- Promote match categories to first-class domain objects (`MatchCategory`) and use them directly in `GameState`, `Match`, and `MatchResult`.
- Hardcode the three existing categories in code and remove the constants dict/order.
- Rename `MatchTypeDefinition` to `MatchType` and have it reference `MatchCategory` objects (not IDs).
- Move match type definitions out of JSON and hardcode them in `wrestlegm/models.py` directly under the class.
- Preserve persistence by keeping category IDs for save/load and UI selection.

**Non-Goals:**
- Changing simulation logic, ratings, or booking rules.
- Introducing new match categories or match types beyond the current set.
- Changing the on-disk save format or adding migrations.

## Decisions

- **Rename models:**
  - `MatchCategoryDefinition` → `MatchCategory`.
  - `MatchTypeDefinition` → `MatchType`.
- **Centralize hardcoded definitions in `wrestlegm/models.py`:**
  - Define the three `MatchCategory` instances directly under the class.
  - Define all `MatchType` instances directly under the class, using `MatchCategory` objects for `allowed_categories`.
- **Canonical registry:**
  - Maintain a single in-memory registry (e.g., list + dict) of `MatchCategory` objects in `wrestlegm/models.py` to avoid duplicate instances and allow stable identity-based comparisons.
- **Ordering:**
  - Remove `MATCH_CATEGORY_ORDER` and derive order from the canonical list in `wrestlegm/models.py`, which is explicitly defined as `singles`, `triple-threat`, `fatal-4-way`.
- **Object usage:**
  - Update `Match` and `MatchResult` to carry a `MatchCategory` object, not an ID string.
  - Retain `match_category_id` at serialization boundaries and map IDs to canonical objects on load or construction.
- **Data loading:**
  - Remove JSON-based match type loading and replace it with imports from `wrestlegm/models.py`.

## Risks / Trade-offs

- **[Risk] Hardcoding reduces flexibility** → Mitigation: keep the definitions centralized and clearly structured in `wrestlegm/models.py` to make future changes straightforward.
- **[Risk] Object identity mismatches** (if categories are re-instantiated) → Mitigation: use a canonical registry and map IDs to those instances everywhere.
- **[Risk] Persistence mapping errors** when converting IDs to objects → Mitigation: keep the save format unchanged and centralize ID-to-object mapping in one place.
- **[Trade-off] Moving match types out of JSON** reduces data-driven configurability → Mitigation: accept this for now to align with the hardcoded category approach and reduce cross-file coupling.

## Migration Plan

- Introduce `MatchCategory` and `MatchType` renames in `wrestlegm/models.py` and define canonical registries under those classes.
- Update `WrestleGMApp`, `SessionManager`, and `GameState` to use the hardcoded lists instead of JSON-loading functions.
- Update all call sites that referenced `constants.MATCH_CATEGORIES` / `MATCH_CATEGORY_ORDER` to use the new registries.
- Update persistence serialization/deserialization to store IDs but hydrate `Match` / `MatchResult` with `MatchCategory` objects.
- Remove `MATCH_CATEGORIES` and `MATCH_CATEGORY_ORDER` from `wrestlegm/constants.py` and eliminate `match_types.json` loading usage.

## Open Questions

- None at this time.
