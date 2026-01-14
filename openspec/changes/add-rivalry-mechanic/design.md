## Context
Rivalries introduce persistent, pairwise state that affects match ratings and show-to-show progression. The system must remain deterministic and apply changes at show boundaries.

## Goals / Non-Goals
- Goals: deterministic rivalry progression per wrestler pair, rating bonuses/penalties, emoji-only UI visibility.
- Non-Goals: manual rivalry creation, rivalry decay, promo-based progression, UI explanations, rivalry screens.

## Decisions
- Pair identity uses a normalized key of the two wrestler IDs (sorted) to ensure deterministic lookups.
- Rivalry progression is 100% when a pair appears in a match and is not in cooldown; each appearance increments `rivalry_value` by 1 and sets `rivalry_level = min(4, rivalry_value)`.
- A match is a blowoff when the pair is already at Level 4 at match time; blowoff resolves at show end and starts a 6-show cooldown.
- Rating bonuses are applied per active rivalry pair (+0.25 stars each). Blowoff pairs apply double bonus (+0.5 stars per pair). Bonuses stack linearly.
- Cooldown applies a -1.0 star penalty once per match if any cooldown pair exists in the match. Bonuses and penalty may both apply.
- Emoji ordering follows wrestler pair order derived from the match wrestler list (unique pairs in list order).

## Risks / Trade-offs
- Keeping both rivalry_value and rivalry_level introduces redundant state; the level is derived to avoid drift.
- Multi-wrestler matches can surface many emojis; ordering is fixed to avoid ambiguity.

## Migration Plan
- New rivalry and cooldown state are introduced with empty initial state. Existing saves should default to no rivalries.

## Open Questions
- None (current rules fixed by request).
