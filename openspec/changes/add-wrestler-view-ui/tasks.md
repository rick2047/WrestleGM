## 1. Implementation
- [ ] 1.1 Extend wrestler data model and loaders for description + avatar_path
- [ ] 1.2 Replace `data/wrestlers.json` with new roster entries mapped to `data/images/01.png`-`10.png`, generate <=80-char descriptions from `data/images/description.md`, and wire default/placeholder paths
- [ ] 1.3 Add Wrestler View widget with configurable blocks and empty-state behavior
- [ ] 1.4 Implement avatar rendering with rich-pixels half renderer and safe fallback to default image
- [ ] 1.5 Redesign Match Booking screen into a single card with inline wrestler-count selection and rivalry summary header
- [ ] 1.6 Update Promo Booking to use a single Wrestler View without rivalry block
- [ ] 1.7 Add Wrestler Selection inspect modal (read-only) and `i` binding with focus restore
- [ ] 1.8 Update UI flows to remove match category selection screen where applicable
- [ ] 1.9 Update UI snapshot tests, flow tests, and fixtures; regenerate baselines

## 2. Validation
- [ ] 2.1 Run unit/UI tests and confirm snapshot updates
- [ ] 2.2 Verify narrow terminal layouts (<=40 columns) for new booking cards
