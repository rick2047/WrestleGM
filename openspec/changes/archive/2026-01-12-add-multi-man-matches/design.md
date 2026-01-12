## Context
WrestleGM currently models matches as 1v1 with match types lacking wrestler count metadata. Issue #28 requires multi-man formats (2–4 wrestlers) while keeping determinism, show structure, and UI patterns intact.

## Goals / Non-Goals
- Goals: add multi-man match support across data, simulation, validation, and UI booking flows; keep deterministic outcomes and minimal UI changes.
- Non-Goals: tag/team logic, new show slot types, rivalry systems, or match-size-based scaling of deltas.

## Decisions
- **Match types declare size**: add `min_wrestlers`/`max_wrestlers` to match type definitions; default to 2 when omitted.
- **Match stores ordered wrestler IDs**: replace `wrestler_a_id`/`wrestler_b_id` with `wrestler_ids` to preserve booking order and enable silent trimming when match type shrinks.
- **Winner selection**: compute per-wrestler power and convert to probabilities, lerp each toward uniform `1/N` using `outcome_chaos`, normalize, and select with a single RNG draw.
- **Rating modifiers**: keep averaged popularity/stamina inputs; apply alignment modifier based on face/heel counts (all heels, all faces, majority heels, majority faces).
- **Stat deltas**: apply winner deltas once and loser deltas to each non-winner once without scaling by match size.
- **UI flow**: insert a match type selection screen before match booking; match booking shows a row per required wrestler, plus a match type row for retargeting.

## Risks / Trade-offs
- More complex match displays (multiple names) may require wrapping; the UI spec will allow long lines to wrap naturally.
- Changing match type mid-booking silently clears extra rows; this is explicit behavior but could surprise users.

## Migration Plan
- Update match type data and loader to accept size metadata.
- Update models and simulation to operate on wrestler lists.
- Update validation and UI booking flows.
- Add/adjust tests for multi-man cases.

## Open Questions
- None; scope and UX behaviors are fully specified in the issue PRD comment.
