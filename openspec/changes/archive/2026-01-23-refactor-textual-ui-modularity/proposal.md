# Change: Refactor Textual UI into modular packages

## Why
The current Textual UI lives in a single large module, which makes navigation, testing, and maintenance harder as features grow. Splitting the UI into focused modules aligns with the Textual best practices (screens/widgets separation, external CSS) and reduces future merge conflicts.

## What Changes
- Extract the UI into a `wrestlegm/ui/` package with clear submodules for the app, screens, widgets, and shared helpers.
- Move reusable widgets (edge-aware list/table, safe select) into a `widgets/` module.
- Move formatting helpers and draft dataclasses into small, dedicated modules.
- Switch the app to use external TCSS via `CSS_PATH` (no visual changes expected).
- Preserve the public import surface (`from wrestlegm.ui import WrestleGMApp, <screens>`) via re-exports to avoid downstream breakage.

## Impact
- Affected specs: `ui` (internal structure and CSS handling; no UI/UX behavior changes).
- Affected code: `wrestlegm/ui.py`, `main.py`, UI tests under `tests/`.
- UI/UX: no visual or flow changes intended; existing UI mockups remain authoritative.

## Non-Goals
- No new UI features or flow changes.
- No gameplay or simulation logic changes.
- No snapshot baseline changes unless required by CSS path adjustments.

## Risks & Mitigations
- Risk: import path churn in tests and entrypoints.
  Mitigation: keep public exports in `wrestlegm/ui/__init__.py`.
- Risk: CSS load path mismatch.
  Mitigation: add a deterministic CSS path and update tests if needed.

## UI Mockups
No UI/UX changes. Existing UI mockups in `openspec/specs/ui/spec.md` remain unchanged.
