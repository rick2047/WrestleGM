## Context
Booking UI needs higher identity density while remaining readable in narrow terminals. The change introduces a reusable Wrestler View component and avatar rendering from local assets.

## Goals / Non-Goals
- Goals:
  - Single Wrestler View component with configurable blocks and safe empty-state behavior.
  - Deterministic, crash-safe avatar rendering with default and placeholder images.
  - Match Booking as a single card with inline wrestler count selection.
- Non-Goals:
  - Any changes to booking rules, match outcomes, or simulation formulas.
  - Photorealistic portraits or external image fetching.

## Decisions
- Decision: Wrestler View is built from optional blocks (avatar, name+alignment, stats, description, rivalry).
  - Why: Composition keeps the widget reusable across booking, selection, and inspection contexts.
- Decision: Avatar rendering uses rich-pixels half renderer with fallback to `data/images/default.png`.
  - Why: Ensures robust behavior when custom assets are missing or invalid.
- Decision: Match Booking header aggregates rivalry emojis across all unordered pairs and compresses counts with ASCII `xN`.
  - Why: Provides quick intensity read without overflowing narrow headers.

## Alternatives considered
- Multiple per-screen bespoke widgets.
  - Rejected due to duplication and inconsistent behavior.
- Leaving match category selection screen intact.
  - Rejected because it adds an extra step and conflicts with the inline count requirement.

## Risks / Trade-offs
- Rendering rich-pixels images could impact layout width; mitigate by fixed dimensions and fallback.
- Removing the match category selection screen requires careful flow updates to preserve validation logic.

## Migration Plan
- Update data model and roster JSON first, then build Wrestler View, then update screens and tests.

## Open Questions
- None.
