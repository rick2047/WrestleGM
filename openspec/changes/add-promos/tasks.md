## 1. Implementation
- [ ] 1.1 Extend wrestler data loading to include `mic_skill` and add defaults in `data/wrestlers.json`.
- [ ] 1.2 Update domain models for show slots to include promo entries and validation for 3 matches + 2 promos with unique wrestlers.
- [ ] 1.3 Implement promo simulation (rating, variance, deltas) and include promo ratings in show rating aggregation.
- [ ] 1.4 Apply promo deltas and promo stamina recovery in the show applier.
- [ ] 1.5 Update booking hub UI to show five slots and allow promo slot selection.
- [ ] 1.6 Add promo booking screen reusing wrestler selection, with confirmation modal and allow low-stamina selection.
- [ ] 1.7 Update results UI to render promo entries and overall show rating.

## 2. Validation
- [ ] 2.1 Add/update simulation tests for promo rating determinism, deltas, and show rating aggregation.
- [ ] 2.2 Add/update UI tests (if present) for promo slot rendering and booking validation.
- [ ] 2.3 Run `uv run pytest`.
