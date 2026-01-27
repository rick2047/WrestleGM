## 1. Layout primitives

- [ ] 1.1 Add an app-level `Header()` instance and style it for a full-width centered title.
- [ ] 1.2 Add a small header-state API (e.g., screen title + optional badge/context strings) and implement updating it on screen mount/resume.
- [ ] 1.3 Implement an ellipsis strategy for overly-long header titles to keep the header single-line.
- [ ] 1.4 Add standard layout containers for `Body` (`height: 1fr`) and optional `Actions` (pinned above footer) with stable CSS classes.
- [ ] 1.5 Update global CSS so non-modal screens are not globally centered; ensure modals remain centered and content-sized.

## 2. Standard screen base + style guide

- [ ] 2.1 Create a `StandardScreen` base for non-modal screens with a required title and a `compose_body()` hook.
- [ ] 2.2 Add an optional `compose_actions()` hook (button-only actions row) and migrate existing action button groups into it.
- [ ] 2.3 Implement a configurable body layout direction (default vertical) via body container classes.
- [ ] 2.4 Write a concise style guide documenting the layout primitives, CSS classes, and examples for building new screens consistently.

## 3. Migrate screens to the standard layout

- [ ] 3.1 Main Menu: set header title to `Main Menu` and remove the duplicated top-of-screen title widgets.
- [ ] 3.2 Save Slots: set header title to `New Game` / `Load Game` based on mode and remove duplicated title widgets.
- [ ] 3.3 Game Hub: set header title to `Game Hub` and remove duplicated title widgets.
- [ ] 3.4 Booking Hub: set header title to `Booking Hub`; keep slot list in body and action buttons in the actions row.
- [ ] 3.5 Match Booking: set header title to `Match {N}` and surface aggregated rivalry + cooldown emojis in the header; keep controls/body/actions separation.
- [ ] 3.6 Promo Booking: set header title to `Promo {N}`; keep performer field in body and action buttons in the actions row.
- [ ] 3.7 Wrestler Selection: set header title to the contextual title provided by the parent screen; ensure inspect flow and inline message remain in body.
- [ ] 3.8 Roster: set header title to `Roster Overview`; keep the table in body and Back in actions row.
- [ ] 3.9 Results: set header title to `Show Results`; ensure large results content scrolls in body with Continue in actions row.
- [ ] 3.10 Simulating: set header title to `Simulating`; keep content minimal and non-interactive.
- [ ] 3.11 Guard Screen: set header title to `Viewport Guard`; keep guard message in body and Quit in actions row.

## 4. Verification and docs

- [ ] 4.1 Update `docs/ui.md` to describe the standardized `Header → Body → Actions → Footer` structure and the header content mapping.
- [ ] 4.2 Update UI flow tests as needed (`uv run pytest tests/test_ui_flows.py`) and fix any focus/navigation regressions introduced by the layout changes.
- [ ] 4.3 Run snapshot tests and update baselines intentionally (`uv run pytest tests/test_ui_snapshots.py --snapshot-update`), then re-run without `--snapshot-update`.
