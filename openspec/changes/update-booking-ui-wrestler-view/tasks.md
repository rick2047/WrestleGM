## 1. Implementation
- [ ] 1.1 Add WrestlerDefinition fields (description, avatar_path) in data model and loader with safe defaults.
- [ ] 1.2 Add Wrestler View widget with configurable blocks and avatar fallback handling.
- [ ] 1.3 Update Match Booking UI to card layout with inline wrestler-count selection and rivalry summary header.
- [ ] 1.4 Update Promo Booking UI to use a single Wrestler View (no rivalry block).
- [ ] 1.5 Add Wrestler View inspection modal to wrestler selection ("i" to open, Esc to close).
- [ ] 1.6 Add startup-only viewport guard screen at <70x40 and route gating in app startup.
- [ ] 1.7 Update UI CSS/layout for the new components and layouts.

## 2. Tests
- [ ] 2.1 Update UI test harness viewport to >=70x40 and add guard screen tests.
- [ ] 2.2 Update UI flow tests for new match booking flow (count selection, confirm path).
- [ ] 2.3 Update snapshot registry and baselines for new booking screens and wrestler view modal.

## 3. Docs
- [ ] 3.1 Update documentation to reflect new minimum viewport target and booking UI behavior.

## 4. Validation
- [ ] 4.1 Run `openspec validate update-booking-ui-wrestler-view --strict`.
- [ ] 4.2 Run `uv run pytest` (or targeted UI tests if available).
