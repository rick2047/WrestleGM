## Context

WrestleGM’s Textual UI currently composes each screen independently. All `Screen` instances are globally centered via `wrestlegm/ui/styles.tcss` (`Screen { align: center middle; }`), and most screens manually render title `Static` widgets (often including a repeated `WrestleGM` label) plus a `Footer`.

This leads to two consistency issues:

- Screens do not follow a consistent `header → body → actions → footer` structure (no single, standardized header or consistent actions placement).
- Many screens do not use available vertical space because widgets are sized to content and the overall screen is centered.

The goal of this change is a cohesive, full-width layout where:

- Non-modal screens show a single centered header containing only the screen name.
- Some screens MAY append compact context badges (e.g., rivalry/cooldown emojis) to the header alongside the screen name.
- The header architecture supports adding compact global context derived from game state in the future (e.g., show name/number, save slot name, money) without disrupting the centered screen name.
- The primary content region expands to fill remaining space, keeping the footer pinned to the bottom.
- Modals remain overlay dialogs sized to their content (no full-screen modal framing).

## Goals / Non-Goals

**Goals:**

- Standardize all non-modal screens to `header → body → actions → footer`, with the actions row optional per-screen.
- Render a full-width header on all non-modal screens with the current screen name centered.
- Make the body region expand (`1fr`) so screens use the viewport effectively.
- Use a dedicated body container whose layout direction is configurable per-screen (default vertical) to support future horizontal layouts without rewriting the layout primitives.
- Produce a concise style guide that documents the layout primitives (header/body/actions/footer), the CSS classes used, and examples for building new screens consistently.
- Preserve existing footer behavior (bindings-only, modal-aware) and existing navigation behavior.
- Keep modals as content-sized overlays that appear centered above the current screen.

**Non-Goals:**

- Changing gameplay logic, navigation routes, or bindings beyond what is needed for layout consistency.
- Redesigning individual screen content (copy, fields, ordering) except where required to fit the new layout container.
- Introducing a new theming system or comprehensive restyling beyond layout primitives.
- Making modals full-screen or adding headers/footers to modals.

## Decisions

### 1) Introduce a shared base layout for non-modal screens

**Decision:** Use Textual’s built-in `Header()` widget for the header, and standardize non-modal screens around a shared “standard screen” abstraction that guarantees a consistent `header → body → actions → footer` experience.

**Rationale:** Centralizing the layout contract ensures consistency, reduces duplication (e.g., repeated title `Static` patterns), and keeps the header modular so it can grow beyond “just the screen title” later (e.g., show number, save slot name) without rewriting every screen.

**Alternatives considered:**

- **Per-screen title `Static`**: makes the header explicit per screen but reintroduces drift and makes later header enhancements (adding game context) require touching every screen.
- **Duplicate per-screen containers**: simplest in the moment but reintroduces drift and makes later tweaks tedious.

**Chosen approach:**

- Render a single `Header()` at the app level (configured/styled to be full-width and to show only the current screen name, centered).
- Provide a small, reusable API for screens to set header state (initially `screen_name`, and optionally a compact list of context badges such as rivalry/cooldown emojis for match booking; later extensible to include additional game-state-driven context such as show name/number or currency).
- Use a base `Screen` class (e.g., `StandardScreen`) with a required `TITLE` (or similar), which sets the header state on mount/resume and yields its main widgets into a body container (`height: 1fr`).
- Provide an optional actions row container (pinned above the footer) for screens that need `Button` actions separate from the body.
- Preserve the existing per-screen `Footer()` usage so key bindings remain authoritative and modal-aware.

### 2) Make non-modal screens full-width and top-aligned by default

**Decision:** Update global CSS so non-modal screens are not globally centered, and provide a standard content container that expands.

**Rationale:** The current `Screen { align: center middle; }` causes content to “float” and prevents the UI from feeling like a full-screen product layout. A top-left aligned root plus an explicit expanding content region yields predictable structure and maximum viewport use.

**Alternatives considered:**

- Keep `Screen` centered and add a full-height shell container per screen: works but keeps a surprising global default and adds more per-screen boilerplate.

### 3) Keep modal screens content-sized and centered

**Decision:** Ensure `ModalScreen` alignment is centered and modal panels remain `height: auto` / content-sized.

**Rationale:** Modals should overlay the current screen and remain as big as needed only. This preserves the existing “panel” modal styling and avoids introducing full-screen modal chrome.

**Alternatives considered:**

- Apply the same header/content/footer layout to modals: rejected because it changes modal affordances and violates the requirement for content-sized overlays.

### 4) Content widgets should participate in the expanding region

**Decision:** Prefer that each screen’s primary interactive widget (e.g., `ListView`, `DataTable`, `VerticalScroll`) uses the content container’s available height.

**Rationale:** A `1fr` content region only helps if children can expand or scroll appropriately. This change may require updating some widgets from `height: auto` to `height: 1fr`, and wrapping large `Static` bodies (e.g., results) in scroll containers where necessary.

**Alternatives considered:**

- Leave all widget heights as-is: would preserve current “floating” look inside an otherwise full-height layout and undermine the primary goal.

## Risks / Trade-offs

- **[Snapshot churn]** UI snapshot tests will change due to layout updates → Mitigation: update snapshots intentionally and keep the layout changes focused to primitives (header + content sizing).
- **[Unexpected widget sizing]** Some widgets may not behave well with `1fr` height by default → Mitigation: adjust CSS per-widget/class and use scroll containers where needed.
- **[Title consistency drift]** If titles remain ad-hoc strings, screens can diverge → Mitigation: make `TITLE` required for `StandardScreen` and keep a small, explicit mapping per screen.

## Migration Plan

- Introduce the base screen abstraction and global CSS updates for `Screen`/`ModalScreen`.
- Migrate each non-modal screen to the new base and remove duplicated top-of-screen title `Static` widgets.
- Verify the footer remains present on all screens and remains modal-aware.
- Update UI documentation (`docs/ui.md`) to reflect the standardized layout.
- Update snapshot baselines in `tests/snapshots/test_ui_snapshots/` after verifying the new layout is correct.

## Open Questions

- Header overflow strategy: titles SHOULD remain single-line; if a title would overflow, it SHOULD be truncated with an ellipsis rather than wrapping.
