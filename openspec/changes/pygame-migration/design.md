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

Screen navigation state machine with automatic rebuilding:

```python
class Router:
    """Manages screen stack and navigation."""
    
    def __init__(self, app: WrestleGMApp) -> None:
        self._app = app
        self._screens: dict[str, type[BaseScreen]] = {}
        self._stack: list[BaseScreen] = []
        self._on_navigate_callback: Optional[Callable] = None
        
    def set_on_navigate_callback(self, callback: Callable) -> None:
        # Set callback invoked after every navigation
        # Used by App to rebuild screen UI
        
    def register(self, route: str, screen_class: type[BaseScreen]) -> None:
        # Register screen class for a route
        
    def navigate(self, route: str, **kwargs) -> None:
        # Push new screen onto stack
        # Call _on_navigate_callback if set
        
    def back(self) -> None:
        # Pop current screen, return to previous
        
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
        self._container = None
        
    def build(self, manager: UIManager, rect: Rect) -> None:
        """Build UI elements in the 4 zones."""
        zones = self._compute_zones(rect)
        self._build_header(manager, zones['header'])
        self._build_body(manager, zones['body'])
        self._build_actions(manager, zones['actions'])
        self._build_footer(manager, zones['footer'])
        
    def handle_event(self, event: Event) -> bool:
        # Handle screen-specific events
        # Return True if consumed
```

## Testing Architecture

### Two-Tier Testing Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    Testing Pyramid                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────┐  ┌─────────────────────────────┐  │
│  │  Screen Tests       │  │  Flow Tests                 │  │
│  │  (Visual)           │  │  (Interaction)              │  │
│  ├─────────────────────┤  ├─────────────────────────────┤  │
│  │ • PNG snapshots     │  │ • Real pygame events        │  │
│  │ • Appearance only   │  │ • Full event flow           │  │
│  │ • Syrupy            │  │ • Navigation verification   │  │
│  │ • One per screen    │  │ • One per user journey      │  │
│  └─────────────────────┘  └─────────────────────────────┘  │
│                                                             │
│  Purpose: Looks correct        Purpose: Works correctly     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Tier 1: Screen Snapshot Testing

**Purpose**: Verify UI appearance matches baseline (visual regression)

**How it works**:
1. Build screen with test data
2. Render to surface
3. Capture as PNG
4. Compare to baseline using Syrupy

**Screen Test Fixture** (`app_with_built_screen`):
```python
@pytest.fixture
def app_with_built_screen():
    """App with pre-built screen ready for snapshot capture."""
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    app = WrestleGMApp()
    app.router.navigate("main_menu")
    screen = app.router.current
    screen.build(app.ui_manager, Rect(0, 0, 480, 800))
    yield app
    pygame.quit()
```

**Screen Test Example**:
```python
def test_main_menu_screen_renders_correctly(
    app_with_built_screen, snapshot_image
):
    """Visual regression test for Main Menu screen."""
    app = app_with_built_screen
    
    # Render UI to surface
    surface = pygame.Surface((480, 800))
    app.ui_manager.draw_ui(surface)
    
    # Convert to PNG bytes
    import io
    buffer = io.BytesIO()
    pygame.image.save(surface, buffer, ".png")
    
    # Compare to baseline
    assert buffer.getvalue() == snapshot_image
```

**Screen Tests Required** (one per screen):
- `test_main_menu_screen_renders_correctly`
- `test_save_slots_screen_renders_correctly`  
- `test_game_hub_screen_renders_correctly`
- `test_booking_hub_screen_renders_correctly`
- `test_match_booking_screen_renders_correctly`
- `test_promo_booking_screen_renders_correctly`
- `test_wrestler_selection_screen_renders_correctly`
- `test_roster_screen_renders_correctly`
- `test_simulating_screen_renders_correctly`
- `test_results_screen_renders_correctly`
- `test_bankruptcy_screen_renders_correctly`

## Tier 2: Flow Testing (Real Interaction)

**Purpose**: Verify user interactions work through full pygame event system

**How it works**:
1. Post real pygame events (MOUSEBUTTONDOWN/UP)
2. Process through UIManager
3. Screen handles UI_BUTTON_PRESSED
4. Verify navigation/state changes

**Flow Test Fixture** (`app_with_interaction`):
```python
@pytest.fixture
def app_with_interaction():
    """App with interaction helpers for testing."""
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    app = WrestleGMApp()
    app.router.navigate("main_menu")
    app.router.current.build(app.ui_manager, Rect(0, 0, 480, 800))
    
    # Track events
    app.events_processed = []
    
    def click(target):
        """Simulate mouse click."""
        pos = target.rect.center if hasattr(target, 'rect') else target
        pygame.event.post(pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, pos=pos, button=1
        ))
        pygame.event.post(pygame.event.Event(
            pygame.MOUSEBUTTONUP, pos=pos, button=1
        ))
        pump_events()
    
    def pump_events():
        """Process all pending events."""
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

**Event Flow in Flow Tests**:
```
Test calls app.click(button):
    ↓
pygame.event.post(MOUSEBUTTONDOWN at button position)
pygame.event.post(MOUSEBUTTONUP at button position)
    ↓
app.pump_events() processes queue:
    ↓
for event in pygame.event.get():
    app.ui_manager.process_events(event)
        ↓
    pygame_gui detects click on button
    pygame_gui posts UI_BUTTON_PRESSED event
        ↓
    app.router.current.handle_event(event)
        ↓
    Screen receives UI_BUTTON_PRESSED
    Screen calls self._router.navigate("next_screen")
        ↓
Router calls on_navigate callback
App rebuilds new screen
    ↓
Test verifies:
    - app.router.current is new screen class
    - New screen has UI elements built
    - Navigation occurred
```

**Flow Tests Required** (one per user journey):

### Flow 1: New Game Creation
```python
def test_new_game_flow(app_with_interaction):
    """Complete new game journey."""
    app = app_with_interaction
    
    # Click NEW GAME button
    app.click(app.router.current._new_game_button)
    
    # Verify: navigated to Save Slots
    assert app.router.current.__class__.__name__ == "SaveSlotSelectionScreen"
    assert app.router.current._mode == "new"
    assert app.router.current._slot_buttons is not None
    
    # Click first empty slot
    app.click(app.router.current._slot_buttons[0])
    
    # Verify: navigated to Game Hub with fresh game
    assert app.router.current.__class__.__name__ == "GameHubScreen"
    assert app._state.show_number == 1  # Fresh game
    assert app.router.current._booking_hub_button is not None
```

### Flow 2: Load Existing Game
```python
def test_load_game_flow(app_with_interaction, populated_save_slot):
    """Load existing game journey."""
    app = app_with_interaction
    
    # Click LOAD GAME button
    app.click(app.router.current._load_game_button)
    
    # Verify: navigated to Save Slots in load mode
    assert app.router.current.__class__.__name__ == "SaveSlotSelectionScreen"
    assert app.router.current._mode == "load"
    
    # Click occupied slot
    app.click(app.router.current._slot_buttons[2])
    
    # Verify: navigated to Game Hub with loaded state
    assert app.router.current.__class__.__name__ == "GameHubScreen"
    assert app._state.show_number > 1  # Not fresh game
```

### Flow 3: Book a Match
```python
def test_book_match_flow(app_with_interaction):
    """Book a match complete journey."""
    app = app_with_interaction
    
    # Navigate to Game Hub first (setup)
    app.router.navigate("game_hub")
    app.pump_events()
    
    # Click BOOKING HUB
    app.click(app.router.current._booking_hub_button)
    assert app.router.current.__class__.__name__ == "BookingHubScreen"
    
    # Click empty match slot
    app.click(app.router.current._slot_buttons[0])
    assert app.router.current.__class__.__name__ == "MatchBookingScreen"
    
    # Click first wrestler slot
    app.click(app.router.current._wrestler_slot_buttons[0])
    assert app.router.current.__class__.__name__ == "WrestlerSelectionScreen"
    
    # Select first available wrestler
    app.click(app.router.current._wrestler_buttons[0])
    assert app.router.current.__class__.__name__ == "MatchBookingScreen"
    
    # Click CONFIRM
    app.click(app.router.current._confirm_button)
    assert app.router.current.__class__.__name__ == "BookingHubScreen"
    
    # Verify: slot now shows match summary
    assert app.router.current._slot_summaries[0] is not None
```

### Flow 4: Complete Show Cycle
```python
def test_complete_show_flow(app_with_interaction):
    """Full show booking to results journey."""
    app = app_with_interaction
    
    # Start at Game Hub with game in progress
    app.router.navigate("game_hub")
    app.pump_events()
    initial_show = app._state.show_number
    
    # Navigate to Booking Hub
    app.click(app.router.current._booking_hub_button)
    
    # Book all 5 slots (simplified - would book each)
    for i in range(5):
        app.click(app.router.current._slot_buttons[i])
        # ... booking logic for each slot ...
        app.click(app.router.current._confirm_button)
    
    # Click RUN SHOW
    app.click(app.router.current._run_show_button)
    assert app.router.current.__class__.__name__ == "SimulatingScreen"
    
    # Wait for simulation (auto-advances)
    # ... time passes ...
    
    # Verify: at Results screen
    assert app.router.current.__class__.__name__ == "ResultsScreen"
    assert app.router.current._show_rating is not None
    
    # Click CONTINUE
    app.click(app.router.current._continue_button)
    assert app.router.current.__class__.__name__ == "GameHubScreen"
    
    # Verify: show number incremented, money updated
    assert app._state.show_number == initial_show + 1
```

### Flow 5: Roster Inspection
```python
def test_roster_inspection_flow(app_with_interaction):
    """View wrestler details from roster."""
    app = app_with_interaction
    
    # Navigate to Game Hub
    app.router.navigate("game_hub")
    app.pump_events()
    
    # Click ROSTER VIEW
    app.click(app.router.current._roster_button)
    assert app.router.current.__class__.__name__ == "RosterScreen"
    
    # Click wrestler row
    app.click(app.router.current._wrestler_panels[0])
    
    # Verify: Inspect modal opened
    assert app.router.current._inspect_modal is not None
    assert app.router.current._inspect_modal._wrestler is not None
    
    # Click CLOSE
    app.click(app.router.current._inspect_modal._close_button)
    
    # Verify: modal closed, back to roster
    assert app.router.current._inspect_modal is None
```

### Flow 6: Save and Quit
```python
def test_save_and_quit_flow(app_with_interaction, tmp_path):
    """Save game and reload journey."""
    app = app_with_interaction
    
    # Navigate to Game Hub
    app.router.navigate("game_hub")
    app.pump_events()
    
    # Make a change (increment show number for tracking)
    initial_show = app._state.show_number
    
    # Click SAVE & QUIT
    app.click(app.router.current._save_quit_button)
    assert app.router.current.__class__.__name__ == "MainMenuScreen"
    
    # Click LOAD GAME
    app.click(app.router.current._load_game_button)
    assert app.router.current.__class__.__name__ == "SaveSlotSelectionScreen"
    
    # Click the slot we saved to
    app.click(app.router.current._slot_buttons[0])
    assert app.router.current.__class__.__name__ == "GameHubScreen"
    
    # Verify: state preserved
    assert app._state.show_number == initial_show
```

### Flow 7: Bankruptcy
```python
def test_bankruptcy_flow(app_with_interaction):
    """Go bankrupt and restart journey."""
    app = app_with_interaction
    
    # Setup: navigate to game with negative money
    app.router.navigate("game_hub")
    app._state.money = -1000  # Force bankruptcy
    app.pump_events()
    
    # Navigate to bankruptcy screen
    app.router.navigate("bankruptcy")
    app.pump_events()
    assert app.router.current.__class__.__name__ == "BankruptcyScreen"
    
    # Click TRY AGAIN
    app.click(app.router.current._try_again_button)
    assert app.router.current.__class__.__name__ == "GameHubScreen"
    
    # Verify: fresh game state
    assert app._state.show_number == 1
    assert app._state.money > 0  # Reset to initial
```

### Flow 8: Back Navigation
```python
def test_back_navigation_flow(app_with_interaction):
    """Navigate deep and use back button."""
    app = app_with_interaction
    
    # Navigate to Save Slots
    app.click(app.router.current._new_game_button)
    assert app.router.current.__class__.__name__ == "SaveSlotSelectionScreen"
    
    # Click back
    app.click(app.router.current._back_button)
    assert app.router.current.__class__.__name__ == "MainMenuScreen"
    
    # Navigate deeper: Main Menu → Save Slots → Game Hub → Booking Hub
    app.click(app.router.current._new_game_button)
    app.click(app.router.current._slot_buttons[0])
    assert app.router.current.__class__.__name__ == "GameHubScreen"
    
    app.click(app.router.current._booking_hub_button)
    assert app.router.current.__class__.__name__ == "BookingHubScreen"
    
    # Go back
    app.click(app.router.current._back_button)
    assert app.router.current.__class__.__name__ == "GameHubScreen"
```

### Flow 9: Error Recovery
```python
def test_error_recovery_flow(app_with_interaction, corrupt_save_slot):
    """Handle corrupt save gracefully."""
    app = app_with_interaction
    
    # Click LOAD GAME
    app.click(app.router.current._load_game_button)
    assert app.router.current.__class__.__name__ == "SaveSlotSelectionScreen"
    
    # Click corrupt slot
    app.click(app.router.current._slot_buttons[2])
    
    # Verify: error modal displayed
    assert app.router.current._error_modal is not None
    assert "corrupt" in app.router.current._error_modal._message.lower()
    
    # Click OK
    app.click(app.router.current._error_modal._ok_button)
    
    # Verify: still on Save Slots, modal closed
    assert app.router.current.__class__.__name__ == "SaveSlotSelectionScreen"
    assert app.router.current._error_modal is None
```

### Flow 10: Cancel Navigation
```python
def test_cancel_navigation_flow(app_with_interaction):
    """Navigate and cancel/back out."""
    app = app_with_interaction
    
    # Go to Save Slots
    app.click(app.router.current._new_game_button)
    assert app.router.current.__class__.__name__ == "SaveSlotSelectionScreen"
    
    # Click CANCEL/BACK
    app.click(app.router.current._back_button)
    
    # Verify: back at Main Menu
    assert app.router.current.__class__.__name__ == "MainMenuScreen"
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
    └───────────────┘
```

## Test Organization

```
tests/ui_pygame/
├── conftest.py                    # Shared fixtures
│   ├── snapshot_image            # PNG snapshot fixture
│   ├── app_with_built_screen     # Screen test fixture
│   └── app_with_interaction      # Flow test fixture
├── screens/
│   ├── test_main_menu_snapshot.py       # Visual regression
│   ├── test_save_slots_snapshot.py
│   ├── test_game_hub_snapshot.py
│   ├── test_booking_hub_snapshot.py
│   ├── test_match_booking_snapshot.py
│   ├── test_promo_booking_snapshot.py
│   ├── test_wrestler_selection_snapshot.py
│   ├── test_roster_snapshot.py
│   ├── test_simulating_snapshot.py
│   ├── test_results_snapshot.py
│   ├── test_bankruptcy_snapshot.py
│   └── __snapshots__/            # Baseline PNG files
├── test_flows.py                  # All 10 flow tests
│   ├── test_new_game_flow
│   ├── test_load_game_flow
│   ├── test_book_match_flow
│   ├── test_complete_show_flow
│   ├── test_roster_inspection_flow
│   ├── test_save_and_quit_flow
│   ├── test_bankruptcy_flow
│   ├── test_back_navigation_flow
│   ├── test_error_recovery_flow
│   └── test_cancel_navigation_flow
├── test_router.py                 # Unit tests
└── test_scaling.py                # Unit tests
```

## Dependencies

```toml
[project]
dependencies = [
    "pygame>=2.5.0",
    "pygame-gui>=0.6.9",
]

[project.optional-dependencies]
test = [
    "pytest>=7.0",
    "syrupy>=5.0",
]
```

## Test Workflow

```bash
# Run all tests
pytest tests/ui_pygame/ -v

# Run only screen tests (visual regression)
pytest tests/ui_pygame/screens/ -v

# Run only flow tests (interaction)
pytest tests/ui_pygame/test_flows.py -v

# Update visual baselines after intentional UI changes
pytest tests/ui_pygame/screens/ --snapshot-update

# Run in CI (headless)
SDL_VIDEODRIVER=dummy pytest tests/ui_pygame/
```
