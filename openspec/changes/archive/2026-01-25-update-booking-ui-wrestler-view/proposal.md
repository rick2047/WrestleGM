# Change: Update booking UI with Wrestler View cards

## Why
Booking screens are currently list-first and information-light. A richer, consistent wrestler identity view will improve booking clarity and player immersion while keeping the UI readable in narrow terminals.

## What Changes
- Add a reusable Wrestler View component with configurable blocks (avatar, header, stats, description, rivalries).
- Redesign Match Booking into a single card layout with inline wrestler-count selection and a rivalry summary header.
- Update Promo Booking to use a single Wrestler View (no rivalry block in this context).
- Add a wrestler inspection modal in selection screens.
- Add a startup viewport guard screen for terminals smaller than 60x30 (check once on launch).
- Extend wrestler data definitions with optional description and avatar_path fields; render avatars via rich-pixels with robust fallbacks.
- Update UI snapshots, flow tests, and viewport tests to cover the new layouts.
- Update documentation to reflect the new minimum viewport target and booking UI behavior.

## Impact
- Affected specs: `ui`, `data`, `ui-testing`, `documentation`
- Affected systems: Textual UI screens/widgets, data loading, UI snapshot baselines, docs

## Non-Goals
- No changes to match outcome logic, simulation rules, rivalry/cooldown mechanics, or booking validation rules.
- No booking advice, projections, or photorealistic images.
