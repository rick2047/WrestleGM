# UI

## Overview
The UI is implemented in `wrestlegm.ui` using Textual. It is keyboard-first,
operates on narrow terminals, and keeps game logic inside `GameState` rather
than in screen classes.

## Flow Summary

Main Menu -> Booking Hub -> Match Booking -> Wrestler/Match Type Selection ->
Confirmation Modal -> Simulating -> Results -> (Continue to Booking Hub or
Roster or Main Menu).

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

### ConfirmBookingModal

Purpose: confirm a booking before committing.

Key bindings:
- `Esc`: cancel

Components:
- `ModalScreen` with a panel containing `Static` prompt and two buttons.

### SimulatingScreen

Purpose: run simulation and advance automatically.

Components:
- `Static` status text.
- `Footer` for bindings (no interaction).

Behavior:
- Calls `GameState.run_show()` on mount and advances after a short timer.

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

### RosterScreen

Purpose: read-only roster view.

Key bindings:
- `Esc`: back

Components:
- `Static` title.
- `ListView` of roster rows with popularity and stamina.
- `Button` back.
- `Footer` for bindings.

## Visual Indicators

- Empty field: "[ Empty ]" or "[ Unset ]" placeholder.
- Fatigue icon: `FATIGUE_ICON` is shown when stamina is at or below the booking limit.
- Block icon: `BLOCK_ICON` is shown in selection messages for invalid choices.

## Validation Rules

- A show must contain exactly three valid matches to run.
- Wrestlers cannot be booked more than once per show.
- Wrestlers below the stamina threshold cannot be booked.
- Validation errors are shown inline on selection screens.
