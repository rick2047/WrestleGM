## 1. Phase 1: Roster data setup
- [x] 1.1 Create the new `data/wrestlers.json` mapped to `data/images/01.png`-`10.png` with <=80-char descriptions from `data/images/description.md`, and wire default/placeholder paths
- [x] 1.2 Ask user to confirm Phase 1 is complete

## 2. Phase 2: Data model + tests
- [x] 2.1 Extend wrestler data model and loaders for description + avatar_path
- [x] 2.2 Add or update tests for the data model changes and make them pass
- [ ] 2.3 Ask user to confirm Phase 2 is complete

## 3. Phase 3: Wrestler View scaffold
- [ ] 3.1 Add Wrestler View widget with configurable blocks and empty-state behavior
- [ ] 3.2 Create a small script to render the Wrestler View for visual inspection
- [ ] 3.3 Implement avatar rendering with rich-pixels half renderer and safe fallback to default image
- [ ] 3.4 Ask user to confirm Phase 3 is complete

## 4. Phase 4: Wrestler View refinements
- [ ] 4.1 Adjust Wrestler View layout and block behavior to match specs
- [ ] 4.2 Ask user to confirm Phase 4 is complete

## 5. Phase 5: UI tests
- [ ] 5.1 Update UI snapshot tests, flow tests, and fixtures; regenerate baselines
- [ ] 5.2 Ask user to confirm Phase 5 is complete

## 6. Phase 6: Screen integration
- [ ] 6.1 Redesign Match Booking screen into a single card with inline wrestler-count selection and rivalry summary header
- [ ] 6.2 Update Promo Booking to use a single Wrestler View without rivalry block
- [ ] 6.3 Add Wrestler Selection inspect modal (read-only) and `i` binding with focus restore
- [ ] 6.4 Update UI flows to remove match category selection screen where applicable
- [ ] 6.5 Ask user to confirm Phase 6 is complete

## 7. Validation
- [ ] 7.1 Run unit/UI tests and confirm snapshot updates
- [ ] 7.2 Verify narrow terminal layouts (<=40 columns) for new booking cards
- [ ] 7.3 Ask user to confirm Validation is complete
