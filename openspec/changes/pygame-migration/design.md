# Design: pygame-migration

## Architecture Overview

The pygame UI maintains separation between presentation and game logic:

```
┌─────────────────────────────────────────────────────────────────┐
│                    pygame Application                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│   │   App       │───▶│   Router    │───▶│   Screen    │         │
│   │   (Main)    │    │   (State)   │    │   (Base)    │         │
│   └─────────────┘    └─────────────┘    └──────┬──────┘         │
│                                                  │               │
│   ┌─────────────┐    ┌─────────────┐            │               │
│   │   UIManager │◄───│   Screen    │◄───────────┘               │
│   │ (pygame_gui)│    │   Instance  │                            │
│   └─────────────┘    └─────────────┘                            │
│                                                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Game Core (UNCHANGED)                         │
│                                                                  │
│   GameState ──▶ validation, simulation, economy                  │
│   SessionManager ──▶ save/load persistence                       │
│   Models ──▶ Wrestler, Match, Show                               │
└─────────────────────────────────────────────────────────────────┘
```

## Package Structure

```
wrestlegm/ui_pygame/
├── __init__.py              # Package exports
├── app.py                   # Main pygame application class
├── router.py                # Screen navigation state machine
├── constants.py             # UI constants (colors, sizes, fonts)
├── theme.py                 # pygame_gui theming configuration
├── screens/
│   ├── __init__.py
│   ├── base.py              # BaseScreen with 4-zone layout
│   ├── main_menu.py
│   ├── save_slots.py
│   ├── game_hub.py
│   ├── booking_hub.py
│   ├── match_booking.py
│   ├── promo_booking.py
│   ├── wrestler_selection.py
│   ├── roster.py
│   ├── simulating.py
│   ├── results.py
│   └── bankruptcy.py
├── widgets/
│   ├── __init__.py
│   ├── header.py            # Standard header with title/info
│   ├── footer.py            # Status/hints bar
│   ├── wrestler_card.py     # Wrestler info display (32×32 + text)
│   ├── match_summary.py     # Match slot preview
│   └── scroll_list.py       # Touch-friendly scrollable list
└── modals/
    ├── __init__.py
    ├── base.py              # Modal base class
    ├── confirm.py           # Yes/No confirmation
    └── error.py             # Error message display
```

## Core Classes

### App (wrestlegm/ui_pygame/app.py)

Entry point and main game loop:

```python
class WrestleGMApp:
    """Main pygame application."""
    
    def __init__(self) -> None:
        # Initialize pygame, create window
        # Load game data, create GameState
        # Initialize pygame_gui UIManager
        # Create Router
        
    def run(self) -> None:
        # Main game loop:
        # 1. Handle events (pygame_gui processes mouse/touch)
        # 2. Update current screen
        # 3. Render (clear → screen.render → present)
        
    @property
    def state(self) -> GameState:
        # Access to game state for screens
```

### Router (wrestlegm/ui_pygame/router.py)

Screen navigation state machine:

```python
class Router:
    """Manages screen stack and navigation."""
    
    def __init__(self, app: WrestleGMApp) -> None:
        self._app = app
        self._screens: dict[str, type[BaseScreen]] = {}
        self._stack: list[BaseScreen] = []
        
    def register(self, route: str, screen_class: type[BaseScreen]) -> None:
        # Register screen class for a route
        
    def navigate(self, route: str, **kwargs) -> None:
        # Push new screen onto stack
        
    def back(self) -> None:
        # Pop current screen, return to previous
        
    def switch(self, route: str, **kwargs) -> None:
        # Replace current screen (no back navigation)
        
    @property
    def current(self) -> BaseScreen:
        # Current top of stack
```

### BaseScreen (wrestlegm/ui_pygame/screens/base.py)

Standard 4-zone layout implementation:

```python
class BaseScreen:
    """Base screen with Header → Body → Actions → Footer layout."""
    
    def __init__(self, app: WrestleGMApp, router: Router) -> None:
        self._app = app
        self._router = router
        self._container = None  # pygame_gui container
        
    def build(self, manager: UIManager, rect: Rect) -> None:
        """Build UI elements in the 4 zones."""
        self._build_header(manager, self._header_rect)
        self._build_body(manager, self._body_rect)
        self._build_actions(manager, self._actions_rect)
        self._build_footer(manager, self._footer_rect)
        
    def _build_header(self, manager: UIManager, rect: Rect) -> None:
        # Title label (left)
        # Info labels (center, right)
        
    def _build_body(self, manager: UIManager, rect: Rect) -> None:
        # Override in subclasses
        # Scrollable content area
        
    def _build_actions(self, manager: UIManager, rect: Rect) -> None:
        # Action buttons (horizontal layout)
        
    def _build_footer(self, manager: UIManager, rect: Rect) -> None:
        # Status/hints label
        
    def update(self, time_delta: float) -> None:
        # Called each frame, update animations/state
        
    def handle_event(self, event: Event) -> bool:
        # Handle screen-specific events
        # Return True if consumed
```

## Layout Calculations

Screen zones computed from design resolution (480×800):

```python
# Design resolution constants
DESIGN_WIDTH = 480
DESIGN_HEIGHT = 800

# Zone heights (at 1× scale)
HEADER_HEIGHT = 50      # ~40-60px
ACTIONS_HEIGHT = 70     # ~60-80px
FOOTER_HEIGHT = 40      # ~30-40px
BODY_HEIGHT = DESIGN_HEIGHT - HEADER_HEIGHT - ACTIONS_HEIGHT - FOOTER_HEIGHT

# Margins/padding (8dp grid)
MARGIN = 8
PADDING = 8

# Computed rectangles (scaled at runtime)
def compute_zones(screen_rect: Rect, scale: float) -> dict[str, Rect]:
    scaled = lambda x: int(x * scale)
    
    return {
        'header': Rect(0, 0, screen_rect.width, scaled(HEADER_HEIGHT)),
        'body': Rect(0, scaled(HEADER_HEIGHT), 
                     screen_rect.width, scaled(BODY_HEIGHT)),
        'actions': Rect(0, scaled(HEADER_HEIGHT + BODY_HEIGHT),
                       screen_rect.width, scaled(ACTIONS_HEIGHT)),
        'footer': Rect(0, scaled(HEADER_HEIGHT + BODY_HEIGHT + ACTIONS_HEIGHT),
                      screen_rect.width, scaled(FOOTER_HEIGHT)),
    }
```

## Scaling Strategy

Runtime scaling to device resolution:

```python
class ScalingManager:
    """Manages UI scaling from design resolution to device."""
    
    def __init__(self, design_size: tuple[int, int], 
                 window_size: tuple[int, int]) -> None:
        self._design = design_size
        self._window = window_size
        # Calculate scale (fit to smallest dimension)
        self._scale = min(
            window_size[0] / design_size[0],
            window_size[1] / design_size[1]
        )
        # Keep integer scale for pixel art
        self._ui_scale = max(1, int(self._scale))
        
    def scale(self, value: int) -> int:
        """Scale a design value to device pixels."""
        return int(value * self._scale)
        
    def ui_scale(self, value: int) -> int:
        """Scale for UI elements (integer only)."""
        return value * self._ui_scale
        
    def letterbox_rect(self) -> Rect:
        """Centered rect maintaining aspect ratio."""
        width = self.scale(DESIGN_WIDTH)
        height = self.scale(DESIGN_HEIGHT)
        x = (self._window[0] - width) // 2
        y = (self._window[1] - height) // 2
        return Rect(x, y, width, height)
```

## Event Handling

Mouse/touch event flow:

```
pygame.MOUSEBUTTONDOWN/MOUSEMOTION/MOUSEBUTTONUP
            │
            ▼
    ┌───────────────┐
    │ UIManager     │  (pygame_gui processes)
    │ process_event │
    └───────────────┘
            │
            ▼
    ┌───────────────┐
    │ UI elements   │  (buttons, lists, etc.)
    │ handle_event  │
    └───────────────┘
            │
            ▼
    ┌───────────────┐
    │ Screen        │  (screen-specific handling)
    │ handle_event  │
    └───────────────┘
            │
            ▼
    ┌───────────────┐
    │ Router        │  (navigation)
    │ (on_button_   │
    │  pressed)     │
    └───────────────┘
```

## Screen Transitions

Simple fade transition between screens:

```python
class TransitionManager:
    """Manages screen transitions."""
    
    def __init__(self) -> None:
        self._active = False
        self._alpha = 0
        self._from_screen = None
        self._to_screen = None
        
    def start(self, from_screen: BaseScreen, to_screen: BaseScreen) -> None:
        self._active = True
        self._from_screen = from_screen
        self._to_screen = to_screen
        self._alpha = 0
        
    FADE_DURATION_SECONDS = 0.3
    
    def update(self, time_delta: float) -> bool:
        if not self._active:
            return True
        self._alpha += int(255 * time_delta / self.FADE_DURATION_SECONDS)
        if self._alpha >= 255:
            self._active = False
            return True
        return False
```

## Dependencies

Add to `pyproject.toml`:

```toml
[project]
dependencies = [
    "pygame>=2.5.0",
    "pygame-gui>=0.6.9",
    # ... existing deps
]
```

## Entry Point Update

`main.py` becomes:

```python
from wrestlegm.ui_pygame import WrestleGMApp

def main() -> None:
    app = WrestleGMApp()
    app.run()

if __name__ == "__main__":
    main()
```

## Testing Strategy

### Real Interaction Testing (NEW)

Unlike mocking or calling methods directly, we simulate real user actions through pygame's event system:

```python
# Minimal example of interaction test
def test_click_new_game_navigates_to_save_slots(app_with_interaction):
    app = app_with_interaction
    
    # Get the NEW GAME button's screen position
    button = app.router.current._new_game_button
    button_center = button.rect.center
    
    # Simulate real mouse click through pygame event system
    pygame.event.post(pygame.event.Event(
        pygame.MOUSEBUTTONDOWN, 
        pos=button_center, 
        button=1
    ))
    pygame.event.post(pygame.event.Event(
        pygame.MOUSEBUTTONUP, 
        pos=button_center, 
        button=1
    ))
    
    # Process events exactly as real app does
    for event in pygame.event.get():
        app.ui_manager.process_events(event)
        app.router.current.handle_event(event)
    
    # Verify navigation happened
    assert app.router.current.__class__.__name__ == "SaveSlotSelectionScreen"
    assert app.router.current._slot_buttons is not None  # Screen was built
```

**The `app_with_interaction` Fixture:**

This pytest fixture creates a headless app with helper methods for interaction testing:

```python
@pytest.fixture
def app_with_interaction():
    """App with interaction helpers for testing real user events.
    
    Provides:
    - app.click(x, y) or app.click(element): Simulate mouse click
    - app.pump_events(): Process all pending events  
    - app.events_processed: List of all events that went through system
    """
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    app = WrestleGMApp()
    app.router.navigate("main_menu")
    app.router.current.build(app.ui_manager, Rect(0, 0, 480, 800))
    
    # Track events
    app.events_processed = []
    
    def click(target):
        """Simulate mouse click at position or on element."""
        pos = target.rect.center if hasattr(target, 'rect') else target
        pygame.event.post(pygame.event.Event(MOUSEBUTTONDOWN, pos=pos, button=1))
        pygame.event.post(pygame.event.Event(MOUSEBUTTONUP, pos=pos, button=1))
        pump_events()
    
    def pump_events():
        """Process all pending events through app."""
        for event in pygame.event.get():
            app.events_processed.append(event)
            app.ui_manager.process_events(event)
            if app.router.current:
                app.router.current.handle_event(event)
    
    app.click = click
    app.pump_events = pump_events
    
    yield app
    pygame.quit()
```

**Event Flow Matches Real User:**
```
Test Code:
  pygame.event.post(MOUSEBUTTONDOWN) 
        ↓
App Code (unchanged):
  for event in pygame.event.get():
      app.ui_manager.process_events(event)  # pygame_gui handles
      app.router.current.handle_event(event)  # Screen receives UI_BUTTON_PRESSED
        ↓
Result: Same code paths as real user click
```

### Flow Testing with Real Interaction

**Testing Philosophy:**
Flow tests use the real interaction approach exclusively. We simulate actual user clicks through pygame's event system rather than calling methods directly. This ensures we're testing the same code paths real users trigger.

**Test Pattern:**
```python
def test_new_game_flow(app_with_interaction):
    app = app_with_interaction
    
    # Start at Main Menu (already built by fixture)
    # Click NEW GAME button
    app.click(app.router.current._new_game_button)
    
    # Verify: navigated to Save Slots
    assert app.router.current.__class__.__name__ == "SaveSlotSelectionScreen"
    assert app.router.current._slot_buttons is not None  # Built successfully
    
    # Click Empty Slot 1 (first available slot)
    app.click(app.router.current._slot_buttons[0])
    
    # Verify: navigated to Game Hub
    assert app.router.current.__class__.__name__ == "GameHubScreen"
    assert app.router.current._booking_hub_button is not None
```

**Detailed Flow Specifications:**

#### Flow 1: New Game Creation
**Path:** Main Menu → Save Slots → Game Hub

**Button Sequence:**
1. **Main Menu:** Click `_new_game_button` (labeled "NEW GAME")
2. **Save Slots:** Click `_slot_buttons[0]` (first empty slot, enabled in "new" mode)
3. **Result:** At Game Hub with fresh game state

**Validations:**
- After click 1: Router.current is SaveSlotSelectionScreen, mode="new"
- After click 2: Router.current is GameHubScreen, state.money is initial amount
- All screens have UI elements built (buttons not None)

#### Flow 2: Load Existing Game
**Path:** Main Menu → Save Slots → Game Hub

**Button Sequence:**
1. **Main Menu:** Click `_load_game_button` (labeled "LOAD GAME")
2. **Save Slots:** Click `_slot_buttons[2]` (occupied slot with save data)
3. **Result:** At Game Hub with loaded game state

**Validations:**
- After click 1: Router.current is SaveSlotSelectionScreen, mode="load"
- After click 2: Router.current is GameHubScreen, state.show_number > 1 (not fresh game)
- Loaded data matches original save

#### Flow 3: Book a Match
**Path:** Game Hub → Booking Hub → Match Booking → Wrestler Selection → (back) → Booking Hub

**Button Sequence:**
1. **Game Hub:** Click `_booking_hub_button` (labeled "BOOKING HUB")
2. **Booking Hub:** Click `_slot_buttons[0]` (first match slot, currently empty)
3. **Match Booking:** Click `_wrestler_slot_buttons[0]` (first wrestler slot)
4. **Wrestler Selection:** Click `_wrestler_buttons[5]` (6th wrestler in list, available)
5. **Match Booking:** Click `_confirm_button` (labeled "CONFIRM")
6. **Result:** Back at Booking Hub, slot 0 now shows match summary

**Validations:**
- After click 1: At Booking Hub, shows 5 empty slots
- After click 2: At Match Booking, category="singles", 2 wrestler slots visible
- After click 3: At Wrestler Selection, roster displayed
- After click 4: Back at Match Booking, wrestler slot 0 now populated
- After click 5: Back at Booking Hub, slot 0 shows wrestler name and match type

#### Flow 4: Complete Show and View Results
**Path:** Game Hub → Booking Hub → [book all 5 slots] → Run Show → Simulating → Results → Game Hub

**Button Sequence:**
1. **Game Hub:** Click `_booking_hub_button`
2. **Booking Hub:** Click `_slot_buttons[0]` (book match 1)
3. **Match Booking:** Select wrestlers, Click `_confirm_button`
4. **Booking Hub:** Click `_slot_buttons[1]` (book match 2)
5. **Match Booking:** Select wrestlers, Click `_confirm_button`
6. **Booking Hub:** Click `_slot_buttons[2]` (book match 3)
7. **Match Booking:** Select wrestlers, Click `_confirm_button`
8. **Booking Hub:** Click `_slot_buttons[3]` (book promo 1)
9. **Promo Booking:** Select wrestler, Click `_confirm_button`
10. **Booking Hub:** Click `_slot_buttons[4]` (book promo 2)
11. **Promo Booking:** Select wrestler, Click `_confirm_button`
12. **Booking Hub:** Click `_run_show_button` (enabled now that all slots full)
13. **Simulating:** Auto-advances after simulation completes
14. **Results:** Click `_continue_button`
15. **Result:** Back at Game Hub with updated money and show number

**Validations:**
- After booking all slots: _run_show_button is enabled (was disabled when incomplete)
- After click 12: At Simulating screen with progress indicator
- After auto-advance: At Results screen showing match outcomes and ratings
- After click 14: At Game Hub, state.show_number incremented, state.money updated

#### Flow 5: Inspect Wrestler from Roster
**Path:** Game Hub → Roster → (click wrestler) → Inspect Modal → (close) → Roster

**Button Sequence:**
1. **Game Hub:** Click `_roster_button` (labeled "ROSTER VIEW")
2. **Roster:** Click `_wrestler_panels[3]` (4th wrestler row)
3. **Inspect Modal:** Click `_close_button` or click outside modal
4. **Result:** Back at Roster, modal closed

**Validations:**
- After click 1: At Roster screen with scrollable list
- After click 2: Inspect modal opens showing wrestler details (stats, rivalries)
- After click 3: Modal closes, back to Roster list

#### Flow 6: Save and Quit
**Path:** Game Hub → (Save & Quit) → Main Menu → Load Game → (verify save)

**Button Sequence:**
1. **Game Hub:** Click `_save_quit_button` (labeled "SAVE & QUIT")
2. **Main Menu:** Click `_load_game_button`
3. **Save Slots:** Click `_slot_buttons[0]` (slot we just saved to)
4. **Result:** At Game Hub with same state as before save

**Validations:**
- After click 1: Back at Main Menu, save file created/updated
- After click 3: At Game Hub, state.show_number matches pre-save value
- State consistency: All game data preserved (roster, history, economy)

### Visual Snapshot Testing with Syrupy

We use **Syrupy** with **PNGImageSnapshotExtension** for deterministic visual regression testing, similar to the existing Textual SVG snapshot approach.

```python
# conftest.py
import pytest
import os
import pygame
from syrupy.extensions.single_file import PNGImageSnapshotExtension

@pytest.fixture
def snapshot_image(snapshot):
    """Snapshot fixture for pygame surface images."""
    return snapshot.use_extension(PNGImageSnapshotExtension)

@pytest.fixture
def pygame_app():
    """Headless pygame app with fixed clock for deterministic testing."""
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    pygame.init()
    
    app = WrestleGMApp()
    app._clock = MockClock(fixed_delta=1/60)  # Fixed timestep
    app._scale = 1.0  # No scaling variation
    
    yield app
    pygame.quit()

# test_screens.py
def test_main_menu_render(pygame_app, snapshot_image):
    """Snapshot test for main menu visual appearance."""
    app = pygame_app
    app.show_screen("main_menu")
    app.process_frame()
    
    # Capture and compare
    import io
    buffer = io.BytesIO()
    pygame.image.save(app.get_screen_surface(), buffer, ".png")
    assert buffer.getvalue() == snapshot_image
```

### Test Organization

```
tests/ui_pygame/
├── conftest.py                # Shared fixtures (pygame_app, snapshot_image)
├── test_router.py             # Unit tests for navigation logic
├── test_scaling.py            # Unit tests for scaling manager
└── screens/                   # Visual snapshot tests per screen
    ├── test_main_menu.py
    ├── test_save_slots.py
    ├── test_game_hub.py
    └── __snapshots__/         # Generated PNG baseline files
        ├── test_main_menu/
        │   └── test_render.png
        └── test_game_hub/
            └── test_render.png
```

### Testing Levels

| Level | Approach | Deterministic? |
|-------|----------|----------------|
| **Unit tests** | Test Router, ScalingManager logic directly | ✅ Yes |
| **Integration tests** | Screen navigation with mock pygame | ✅ Yes |
| **Visual snapshots** | PNG comparison via Syrupy | ✅ Yes (with mock clock) |
| **Game logic** | Existing tests unchanged | ✅ Yes |

### Dependencies

```toml
[project.optional-dependencies]
test = [
    "pytest>=7.0",
    "syrupy>=5.0",
]
```

### Workflow

```bash
# Create initial baselines
pytest tests/ui_pygame/ --snapshot-update

# Verify no regressions (CI)
pytest tests/ui_pygame/

# Update after intentional UI changes
pytest tests/ui_pygame/ --snapshot-update
```

## Technical Decisions

1. **Font**: Bundle a pixel font (e.g., [Press Start 2P](https://fonts.google.com/specimen/Press+Start+2P) or similar open source pixel font)
2. **Image formats**: PNG for pixel art with transparency

## Future Possibilities

1. **Mobile packaging**: Architecture supports Android/iOS builds (e.g., buildozer), but not setting up now
