## Why

The current list-based navigation on hub screens feels dated and can be less intuitive than a direct button-driven interface. This change aims to modernize the user experience by replacing these lists with clear, distinct buttons for each action.

## What Changes

- The `ListView` on the `MainMenuScreen` will be replaced with individual `Button` widgets.
- The `ListView` on the `GameHubScreen` will be replaced with individual `Button` widgets.
- The primary slot selection `ListView` on the `BookingHubScreen` will be replaced with a series of `Button` widgets, one for each booking slot.
- The save/load slot selection list will be converted to a button-driven menu.
- Promo slots on the booking hub will include the wrestler alignment emoji in their summary.
- The roster overview will support an inspect action to view detailed wrestler info.

## Capabilities

### New Capabilities
*(none)*

### Modified Capabilities
- `ui`: The core navigation paradigm for hub screens is changing from scroll-and-select (`ListView`) to a direct-activation, button-focused model.

## Impact

- `wrestlegm/ui/screens/main_menu.py`
- `wrestlegm/ui/screens/game_hub.py`
- `wrestlegm/ui/screens/booking_hub.py`
- `wrestlegm/ui/screens/save_slots.py`
- `wrestlegm/ui/screens/roster.py`
