# Design: Modular Textual UI Layout

## Overview
Refactor the monolithic `wrestlegm/ui.py` into a package that separates the App, Screens, Widgets, and shared helpers. This keeps UI code organized, aligns with Textual conventions, and makes it easier to extend or test screens in isolation.

## Package Layout
Proposed layout (exact filenames can vary slightly to keep screens grouped logically):

```
wrestlegm/
  ui/
    __init__.py          # Public re-exports for app/screens/modals/widgets
    app.py               # WrestleGMApp (entry point + CSS path)
    styles.tcss          # Extracted CSS (no visual change)
    formatting.py        # build_name_cell, build_pop_cell, format_stars, etc.
    drafts.py            # BookingDraft, PromoDraft
    widgets/
      __init__.py
      list_views.py      # EdgeAwareListView, FilteredListView
      data_table.py      # EdgeAwareDataTable
      safe_select.py     # SafeSelect
    screens/
      __init__.py
      main_menu.py
      save_slots.py      # SaveSlotSelectionScreen, NameSaveSlotModal, OverwriteSaveSlotModal
      game_hub.py
      booking_hub.py
      match_booking.py
      promo_booking.py
      wrestler_selection.py
      match_category_selection.py
      results.py
      simulating.py
      roster.py
      modals.py          # ConfirmBookingModal, ErrorModal (optional split)
```

## Responsibilities & Boundaries
- `app.py` owns app lifecycle, data/session initialization, and screen routing.
- `screens/` modules contain only the UI logic for that screen or modal.
- `widgets/` contains reusable custom widgets with no game-state knowledge.
- `formatting.py` encapsulates UI string formatting (icons, star ratings, labels).
- `drafts.py` holds state-only draft objects used by booking screens.
- `__init__.py` re-exports the public API to preserve imports used by `main.py` and tests.

## CSS Strategy
- Move inline `CSS` to `styles.tcss` and set `WrestleGMApp.CSS_PATH` to that file.
- Keep CSS unchanged to avoid visual diffs and snapshot churn.

## Textual Guidelines Applied
- Separation of concerns (screens vs widgets vs helpers).
- Prefer composition inside screens; avoid cross-screen coupling.
- External CSS for clearer UI/logic separation.

## Testing Impact
- Preserve public import surface via re-exports so existing tests can keep `from wrestlegm.ui import ...`.
- Update any tests or fixtures that rely on file paths (if any) once CSS moves to a `.tcss` file.
- No functional changes expected; snapshot diffs should not occur if CSS remains identical.
