## Technical Design

This change will be implemented by replacing `textual.widgets.ListView` components with `textual.widgets.Button` components in three key screens. The core logic will shift from handling `ListView.Selected` events to handling `Button.Pressed` events. Keyboard navigation between options will be preserved by explicitly managing focus movement across buttons, mirroring the prior list navigation behavior. Layout will be updated so the button groups are centered and expand to better fill the screen, giving a more game-like presentation on large displays. At the layout level, `StandardScreen` will center its body content by default so screens are not clustered in the top-left on large viewports.

### 1. `MainMenuScreen` (`wrestlegm/ui/screens/main_menu.py`)

-   **Current:** Uses an `EdgeAwareListView` to display `ListItem` widgets for "New Game", "Load Game", and "Quit".
-   **Proposed:**
    -   The `compose_body` method will be updated to `yield` three `Button` widgets, one for each menu option.
    -   The `on_list_view_selected` event handler will be replaced with an `on_button_pressed` handler. This new handler will inspect the `event.button.id` to determine which action to take (e.g., `self.app.navigate(...)` or `self.app.exit()`).
    -   The `on_mount` method, which was used to focus the list, will be removed as it is no longer necessary.

### 2. `GameHubScreen` (`wrestlegm/ui/screens/game_hub.py`)

-   **Current:** Uses an `EdgeAwareListView` to display options.
-   **Proposed:**
    -   Similar to the main menu, `compose_body` will be changed to `yield` `Button` widgets for "Book Current Show", "Roster Overview", and "Exit to Main Menu".
    -   The `on_list_view_selected` handler will be replaced with an `on_button_pressed` handler that routes to the correct screen based on the pressed button's ID.
    -   The `refresh_view` method will be updated to set the `.label` property of the "Book Current Show" button directly, instead of updating a `Static` widget within a list item.

### 3. `BookingHubScreen` (`wrestlegm/ui/screens/booking_hub.py`)

-   **Current:** Uses an `EdgeAwareListView` to display the 5 show slots.
-   **Proposed:**
    -   The `compose_body` method will loop from 0 to `constants.SHOW_SLOT_COUNT` and `yield` a `Button` for each slot. Each button will have a unique ID like `slot-button-0`.
    -   The `refresh_view` method will be updated. Instead of updating `Static` widgets inside a list, it will now update the `.label` of each of the 5 `Button` widgets using the existing `slot_text` helper method.
    -   The `on_list_view_selected` and `action_edit_slot` handlers will be replaced. A new `on_button_pressed` handler will be added. It will parse the button ID (e.g., `slot-button-0`) to get the slot index and then call the appropriate navigation logic (e.g., `self.open_match_booking(index)`).
    -   Focus management logic (`_move_focus`) will need to be updated to cycle through the new slot buttons and the existing "Run Show" and "Back" buttons.

### 4. `SaveSlotSelectionScreen` (`wrestlegm/ui/screens/save_slots.py`)

-   **Current:** Uses a `FilteredListView` populated with `ListItem` rows for save/load slots.
-   **Proposed:**
    -   Replace the list view with a vertical group of `Button` widgets, one per save slot, mirroring the slot label text.
    -   Disabled state should reflect load mode restrictions (non-existent slots should be disabled when loading).
    -   Replace `on_list_view_selected` and list cursor logic with `on_button_pressed` handling and focus cycling over the slot buttons.
    -   Keep the existing slot labeling logic and overwrite flow unchanged; only the selection UI and focus behavior change.

### 5. `BookingHubScreen` Promo Alignment (`wrestlegm/ui/screens/booking_hub.py`)

-   **Current:** Promo slot summaries show the wrestler name only.
-   **Proposed:** Include the alignment emoji alongside the wrestler name in promo slot summaries, using the same alignment emoji mapping used elsewhere in the UI.

### 6. `RosterScreen` Inspect Action (`wrestlegm/ui/screens/roster.py`)

-   **Current:** Roster overview is read-only with only a Back action.
-   **Proposed:**
    -   Add an inspect binding (e.g., `i`) that opens a read-only wrestler inspection modal for the highlighted roster entry.
    -   Reuse the existing wrestler inspection modal behavior from the selection screen to avoid duplicating the view layout.
    -   Restore focus to the roster table after closing the modal, keeping the previously highlighted row selected.
