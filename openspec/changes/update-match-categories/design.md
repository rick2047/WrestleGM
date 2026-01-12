## Context
Match size and match rules are currently coupled through match types. The booking flow uses match type to determine the number of wrestler slots, and the match type list mixes size and rules. We want a separate match category (size) selection to enable combinations like Triple Threat Hardcore.

## Goals / Non-Goals
- Goals:
  - Separate match category (size) from match type (rules).
  - Keep simulation formulas generalized to any wrestler count.
  - Allow match types to be restricted to specific categories.
  - Present category + match type together in booking hub and results.
- Non-Goals:
  - Rebalance simulation modifiers.
  - Add new categories beyond Singles/Triple Threat/Fatal 4-Way.

## Decisions
- Decision: Introduce a fixed match category list in code with explicit wrestler counts.
  - Rationale: Categories are small, stable, and can be expanded later without a data migration.
- Decision: Keep match types data-driven and add an optional `allowed_categories` list.
  - Rationale: Match types are data content; the restriction belongs to type configuration.
- Decision: Store both `match_category_id` and `match_type_id` on `Match`.
  - Rationale: Category is a booking choice needed for validation and display even if type changes.

## Risks / Trade-offs
- Risk: Existing snapshots and UI flows will need updates due to new category selection and extra line items.
- Risk: Validation must ensure match types remain compatible when categories change.

## Migration Plan
- Add a fixed category registry (Singles=2, Triple Threat=3, Fatal 4-Way=4).
- Extend match types with `allowed_categories` (default all).
- Add `match_category_id` to matches and update booking flow/validation.
- Update UI flows and snapshot baselines.

## Open Questions
- Should category names appear anywhere else (e.g., show card exports)?
