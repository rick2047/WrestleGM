## 1. Implementation
- [x] 1.1 Define match categories (Singles/Triple Threat/Fatal 4-Way) with wrestler counts and labels.
- [x] 1.2 Add `match_category_id` to match models/state and persist it through booking, simulation, and results.
- [x] 1.3 Update stipulation data to include `allowed_categories` and add the Ambulance type (Singles-only).
- [x] 1.4 Update booking flow to: category selection screen → match booking with stipulation dropdown filtered by category.
- [x] 1.5 Update booking hub and results display to show `Category · Stipulation` for matches.
- [x] 1.6 Update validation to enforce category wrestler counts and stipulation/category compatibility.

## 2. Tests
- [x] 2.1 Add/adjust unit tests for category-based validation and type restrictions.
- [x] 2.2 Update UI flow tests for category selection and stipulation dropdown behavior.
- [x] 2.3 Regenerate UI snapshot baselines for booking hub, match booking, category selection, and results.
