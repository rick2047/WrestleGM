## Context
The booking UI currently renders text-first lists and uses separate selection screens. The new design requires richer wrestler identity presentation, consistent composition across booking/selection contexts, and a minimum terminal viewport guard at startup. The solution must follow Textual best practices for composition, styling, and deterministic testing.

## Goals / Non-Goals
- Goals:
  - Introduce a reusable Wrestler View widget with configurable blocks per context.
  - Keep booking layouts stable within the 60x30 minimum viewport.
  - Ensure avatar rendering never crashes the UI and has reliable fallbacks.
  - Maintain keyboard-only navigation and deterministic UI tests.
- Non-Goals:
  - No changes to simulation logic or booking validation rules.
  - No advice or projections in the UI.

## Decisions
- Decision: Create a dedicated `WrestlerView` widget rather than reusing ad-hoc `Static` text.
  - Why: Composition keeps layout consistent, encourages reuse across screens, and aligns with Textual's component model.
- Decision: Configure Wrestler View via explicit flags/props for each block (avatar, header, stats, description, rivalries).
  - Why: Clear, explicit configuration avoids implicit coupling and supports booking vs inspection presets.
- Decision: Use `Static` (cached render) for avatar + header + stat lines and avoid expensive recomposition.
  - Why: Textual best practice for performance and stable snapshots.
- Decision: For avatar rendering, cache loaded image data and fall back to a default avatar if decoding fails.
  - Why: Avoid UI crashes and repeated decode overhead.
- Decision: Add a startup-only viewport guard in `App.on_mount()`.
  - Why: Aligns with Textual lifecycle; avoids runtime resize churn.

## Alternatives Considered
- Alternative: Keep list-based booking screens with richer text-only formatting.
  - Rejected: Hard to match desired layout and inspection modal requirements.
- Alternative: Use a single monolithic booking widget instead of reusable Wrestler View.
  - Rejected: Less reusable and harder to maintain.

## Risks / Trade-offs
- Risk: Avatar rendering costs could slow UI refresh.
  - Mitigation: Cache decoded images and keep renders in `Static` widgets.
- Risk: Large layout changes will require snapshot and flow test updates.
  - Mitigation: Update snapshots and add targeted UI tests during implementation.
- Risk: Minimum viewport change conflicts with prior project guidance.
  - Mitigation: Update documentation and UI spec to reflect 60x30 baseline.

## Migration Plan
1) Add spec deltas for UI/data/test/docs.
2) Implement Wrestler View widget and update booking/selection screens.
3) Update UI tests and snapshots.
4) Update documentation and verify viewport guard behavior.

## Open Questions
- None.
