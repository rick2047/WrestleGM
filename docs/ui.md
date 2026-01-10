# UI

## Overview
The UI is implemented in `wrestlegm.ui` using Textual. It is keyboard-first,
operates on narrow terminals, and keeps game logic inside `GameState` rather
than in screen classes.

## Flow Summary

Main Menu -> Booking Hub -> Match Booking -> Wrestler/Match Type Selection ->
Confirmation Modal -> Simulating -> Results -> (Continue to Booking Hub or
Roster or Main Menu).

## Navigation Model

- Each screen is a `Screen` or `ModalScreen` pushed onto Textual's stack.
- Selection screens pop back to the parent on choose/cancel.
- Results and booking screens use explicit actions rather than implicit back.

## Global Components

- `Footer`: always present, shows key bindings only.
- `ListView` + `ListItem`: used for menu lists, match slots, and selections.
- `Button`: actions such as Run Show, Confirm, and Back.
- `Static`: labels, detail lines, and status text.
- `Horizontal` / `Vertical`: lightweight layout containers.

## Screens and Composition

### MainMenuScreen

Purpose: entry point and global navigation.

Key bindings:
- `Enter`: select
- `q`: quit

Components:
- `ListView` with items for New Game, Roster Overview, and Quit.
- `Footer` for bindings.

State interactions:
- `New Game` switches to `BookingHubScreen` with current `GameState`.
- `Roster Overview` pushes `RosterScreen` without changing state.
- `Quit` calls `App.exit()`.

Focus behavior:
- The menu list receives focus on mount.

### BookingHubScreen

Purpose: show overview and match slot selection.

Key bindings:
- `Enter`: edit slot
- `r`: run show
- `Esc`: back

Components:
- `Static` title and show header.
- `ListView` of three slot items.
- `Button` group for Run Show and Back.
- `Footer` for bindings.

Behavior:
- Run Show is disabled until all slots are valid.
- Slot text shows match card details or empty placeholders.

State interactions:
- Pulls `show_index` and `show_card` from `GameState`.
- Uses `GameState.validate_show()` to enable or disable Run Show.
- Pushes `MatchBookingScreen` for the selected slot.

Focus behavior:
- The slot list receives focus on mount.

### MatchBookingScreen

Purpose: edit a single match slot.

Key bindings:
- `Enter`: select field
- `Esc`: cancel

Components:
- `Static` header and detail line.
- `ListView` fields: Wrestler A, Wrestler B, Match Type.
- `Button` group: Confirm, Clear Slot, Cancel.
- `Footer` for bindings.

Behavior:
- Confirm requires all fields and no validation errors.
- Clear Slot removes the match from the slot.
- Validation logic runs through `GameState` to prevent duplicates or invalid
  stamina bookings.

State interactions:
- Loads existing match data from `GameState.show_card` into a local draft.
- Draft selections update only local state until confirmed.
- Confirm opens `ConfirmBookingModal`, which calls `GameState.set_slot()` on accept.

Focus behavior:
- The field list receives focus on mount.

### WrestlerSelectionScreen

Purpose: pick a wrestler for a match slot.

Key bindings:
- `Enter`: select
- `Esc`: cancel

Components:
- `Static` header.
- `ListView` of wrestler rows with alignment and stamina.
- `Static` message line for validation errors.
- `Button` group: Select, Cancel.
- `Footer` for bindings.

Behavior:
- Prevents selecting the same wrestler twice in a match.
- Blocks wrestlers already booked in another slot.
- Blocks wrestlers below the booking stamina threshold.

State interactions:
- Lists all wrestlers from `GameState.roster`.
- Calls `GameState.is_wrestler_booked()` for cross-slot checks.
- Uses the selection callback to update the booking draft.

Focus behavior:
- The wrestler list receives focus on mount.

### MatchTypeSelectionScreen

Purpose: pick a match type for a slot.

Key bindings:
- `Enter`: select
- `Esc`: cancel

Components:
- `Static` header.
- `ListView` of match type names.
- `Static` description panel updated on highlight.
- `Button` group: Select, Cancel.
- `Footer` for bindings.

Behavior:
- Highlighting updates the description panel.
- Selection uses the callback to update the booking draft.

State interactions:
- Lists match types from `GameState.match_types`.

Focus behavior:
- The match type list receives focus on mount.

### ConfirmBookingModal

Purpose: confirm a booking before committing.

Key bindings:
- `Esc`: cancel

Components:
- `ModalScreen` with a panel containing `Static` prompt and two buttons.

State interactions:
- Returns a boolean to the parent screen to commit or discard the draft.

### SimulatingScreen

Purpose: run simulation and advance automatically.

Components:
- `Static` status text.
- `Footer` for bindings (no interaction).

Behavior:
- Calls `GameState.run_show()` on mount and advances after a short timer.

State interactions:
- Updates `GameState.last_show` and advances `show_index`.
- Clears the show card for the next booking phase.

### ResultsScreen

Purpose: display match outcomes and show rating.

Key bindings:
- `Enter`: continue
- `r`: roster
- `m`: main menu

Components:
- `Static` title.
- `Static` results list with star ratings.
- `Static` show rating summary.
- `Button` group: Continue, Roster, Main Menu.
- `Footer` for bindings.

State interactions:
- Reads `GameState.last_show` to populate match results and show rating.
- Continue switches back to `BookingHubScreen` with updated state.

Focus behavior:
- No list focus is required; actions are bound to buttons and keys.

### RosterScreen

Purpose: read-only roster view.

Key bindings:
- `Esc`: back

Components:
- `Static` title.
- `ListView` of roster rows with popularity and stamina.
- `Button` back.
- `Footer` for bindings.

State interactions:
- Reads `GameState.roster` for current popularity/stamina values.

Focus behavior:
- The roster list receives focus on mount.

## Visual Indicators

- Empty field: "[ Empty ]" or "[ Unset ]" placeholder.
- Fatigue icon: `FATIGUE_ICON` is shown when stamina is at or below the booking limit.
- Block icon: `BLOCK_ICON` is shown in selection messages for invalid choices.

## Validation Rules

- A show must contain exactly three valid matches to run.
- Wrestlers cannot be booked more than once per show.
- Wrestlers below the stamina threshold cannot be booked.
- Validation errors are shown inline on selection screens.
