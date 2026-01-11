# Change: Show popularity and alignment emoji in wrestler selection

## Why
The wrestler selection screen currently shows only alignment initial and stamina, which makes it harder to compare choices quickly while booking. Adding popularity and a clear alignment emoji improves scanability without changing game logic.

## What Changes
- Show popularity and alignment emoji alongside stamina in wrestler selection rows.
- Add a table header row naming the columns (name, stamina, popularity).
- Format each selection row as: `{emoji} {name:<18} {sta:>3} {pop:>3}{fatigue}{booked_marker}`.
- Truncate names longer than 18 characters to 15 + `...` so columns stay aligned.
- Render the wrestler selection list as a Textual table so columns align even with emoji width.
- Apply the same table layout, header, and row formatting to the roster overview screen.
- Missing values are not expected; the UI continues to assume alignment, popularity, and stamina are present per the data spec.

Mockup:
```markdown
| Name                   | Sta | Pop |
|:-----------------------|----:|----:|
| 😃 Nova Blaze          |  92 |  87 |
| 😈 Razor King          |  45 |  63 📅 |
| 😃 Longnamed Wrestler... |  08 |  54 🥱 |
```
- Standardize alignment emoji mapping: Face uses 😃, Heel uses 😈.

## Impact
- Affected specs: ui
- Affected code: `wrestlegm/ui.py` (wrestler selection list rendering)
