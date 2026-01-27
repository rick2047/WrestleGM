## Technical Design

This change will be implemented by replacing `textual.widgets.ListView` components with `textual.widgets.Button` components in three key screens. The core logic will shift from handling `ListView.Selected` events to handling `Button.Pressed` events.

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

-   **Current:** Uses an `EdgeAwareListView` to display the 7 show slots.
-   **Proposed:**
    -   The `compose_body` method will loop from 0 to `constants.SHOW_SLOT_COUNT` and `yield` a `Button` for each slot. Each button will have a unique ID like `slot-button-0`.
    -   The `refresh_view` method will be updated. Instead of updating `Static` widgets inside a list, it will now update the `.label` of each of the 7 `Button` widgets using the existing `slot_text` helper method.
    -   The `on_list_view_selected` and `action_edit_slot` handlers will be replaced. A new `on_button_pressed` handler will be added. It will parse the button ID (e.g., `slot-button-0`) to get the slot index and then call the appropriate navigation logic (e.g., `self.open_match_booking(index)`).
    -   Focus management logic (`_move_focus`) will need to be updated to cycle through the new slot buttons and the existing "Run Show" and "Back" buttons.
