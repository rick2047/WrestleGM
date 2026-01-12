## 1. Implementation
- [ ] 1.1 Define match categories (Singles/Triple Threat/Fatal 4-Way) with wrestler counts and labels.
- [ ] 1.2 Add `match_category_id` to match models/state and persist it through booking, simulation, and results.
- [ ] 1.3 Update match type data to include `allowed_categories` and add the Ambulance type (Singles-only).
- [ ] 1.4 Update booking flow to: category selection screen → match booking with match type dropdown filtered by category.
- [ ] 1.5 Update booking hub and results display to show `Category · Type` for matches.
- [ ] 1.6 Update validation to enforce category wrestler counts and match type/category compatibility.

## 2. Tests
- [ ] 2.1 Add/adjust unit tests for category-based validation and type restrictions.
- [ ] 2.2 Update UI flow tests for category selection and match type dropdown behavior.
- [ ] 2.3 Regenerate UI snapshot baselines for booking hub, match booking, category selection, and results.
