## 1. Implementation
- [x] 1.1 Update wrestler selection row formatting to include popularity and alignment emoji mapping (Face 😃, Heel 😈).
- [x] 1.2 Truncate long names to 18 characters (15 + `...`) to preserve column alignment.
- [x] 1.3 Add a selection list header row with column names (excluding alignment).
- [x] 1.4 Ensure low-stamina and booked indicators still render correctly.
- [x] 1.5 Update the roster overview list formatting to match the selection list header and row layout.
- [x] 1.6 Ensure roster rows use the same emoji mapping and truncation rules.
- [x] 1.7 Add/adjust UI tests if coverage exists for selection row formatting.
- [x] 1.8 Refactor selection list to a Textual table while preserving keyboard selection behavior.
- [x] 1.9 Refactor roster overview list to a Textual table and reuse the same columns.
- [x] 1.10 Align table columns with the emoji-prefixed name, stamina, and popularity cells.

## 2. Validation
- [ ] 2.1 Open the wrestler selection screen from match booking and confirm the header row aligns with the columns.
- [ ] 2.2 Verify alignment emoji appears before the name and uses 😃 for Face and 😈 for Heel.
- [ ] 2.3 Confirm stamina and popularity render as numbers only, in the expected columns.
- [ ] 2.4 Verify long names truncate to 15 + `...` and columns stay aligned.
- [ ] 2.5 Confirm 🥱 appears for low-stamina wrestlers and 📅 appears for booked wrestlers.
- [ ] 2.6 Open the roster overview screen and confirm the header row aligns with the columns.
- [ ] 2.7 Verify roster rows follow the same emoji/name/stamina/popularity layout as the selection list.
