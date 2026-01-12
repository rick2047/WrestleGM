## 1. Implementation
- [x] 1.1 Extend wrestler data loading to include `mic_skill` and add defaults in `data/wrestlers.json`.
- [x] 1.2 Update test data fixtures to include `mic_skill` values where applicable.
- [x] 1.3 Update domain models for show slots to include promo entries and validation for 3 matches + 2 promos with unique wrestlers.
- [x] 1.4 Implement promo simulation (rating, variance, deltas) and include promo ratings in show rating aggregation.
- [x] 1.5 Apply promo deltas and promo stamina recovery in the show applier.
- [x] 1.6 Update booking hub UI to show five slots and allow promo slot selection.
- [x] 1.7 Add promo booking screen reusing wrestler selection, with confirmation modal and allow low-stamina selection.
- [x] 1.8 Update results UI to render promo entries and overall show rating.

## 2. Validation
- [x] 2.1 Add/update simulation tests for promo rating determinism, deltas, and show rating aggregation.
- [x] 2.2 Add/update UI tests (if present) for promo slot rendering and booking validation.
- [x] 2.3 Run `uv run pytest`.
