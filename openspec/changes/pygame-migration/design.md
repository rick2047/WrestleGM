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
├── screens/                 # Screen implementations (4-zone layout)
│   ├── __init__.py
│   ├── base.py              # BaseScreen base class
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
└── assets/                  # Static assets (images, fonts)
    ├── __init__.py
    ├── fonts/               # Pixel fonts (Press Start 2P, etc.)
    └── images/              # 32x32 pixel art, icons
```

**Notes:**
- **widgets/** folder removed - use pygame_gui elements directly (UIPanel, UILabel, UIButton, UIProgressBar, etc.)
- **modals/** folder removed - use pygame_gui.windows directly (UIConfirmationDialog, UIMessageWindow) instead of custom modal classes
- **assets/** folder added for 32x32 pixel art and bundled fonts

**Key Differences from Textual Layout:**
Unlike the textual implementation which required custom widget and modal classes, pygame_gui provides all necessary UI elements out-of-the-box. We use:
- `pygame_gui.elements` for standard UI (buttons, labels, panels, lists)
- `pygame_gui.windows` for modal dialogs (confirmation, message)
- No custom subclasses needed - compose built-in elements directly in screens

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

Screen navigation state machine with automatic rebuilding. The Router manages a stack-based navigation system where screens can be pushed onto the stack (navigate forward), popped off (go back), or replaced. It coordinates with the App to ensure UI elements are rebuilt after each navigation.

**Key Concepts:**
- **Stack-based navigation**: Screens are pushed/popped from a stack, maintaining navigation history
- **Automatic rebuilding**: After each navigation, a callback triggers UI rebuilding so new screens have interactive elements
- **Transition support**: Optional fade transitions between screens with deferred callbacks
- **Route registration**: Screen classes are registered by name, then instantiated during navigation

**Navigation Patterns:**
- `navigate()` - Push new screen onto stack (adds to history)
- `back()` - Pop current screen, return to previous
- `switch()` - Replace current screen (no history entry)
- `navigate_with_transition()` - Push screen with fade animation

```python
class Router:
    """Manages screen stack and navigation with automatic UI rebuilding."""
    
    def __init__(self, app: WrestleGMApp) -> None:
        """Initialize router with empty screen registry and stack.
        
        Sets up storage for registered routes, navigation stack, and
        optional transition/callback managers.
        """
        
    def set_on_navigate_callback(self, callback: Optional[Callable]) -> None:
        """Set default callback invoked after every navigation.
        
        This callback is triggered after a screen is added to the stack,
        allowing the App to build UI elements for the new screen. Used
        for automatic screen rebuilding after navigation.
        """
        
    def set_transition_manager(self, transition_manager) -> None:
        """Set the transition manager for animated navigation.
        
        The transition manager handles fade animations between screens.
        If set, navigate_with_transition() will use it; otherwise
        navigation happens immediately without animation.
        """
        
    def register(self, route: str, screen_class: type[BaseScreen]) -> None:
        """Register a screen class for a named route.
        
        Associates a route name (e.g., "main_menu") with a screen class.
        When navigate() is called with this route, the registered class
        is instantiated to create the screen.
        """
        
    def navigate(self, route: str, *, on_navigate: Optional[Callable] = None, **kwargs) -> None:
        """Push new screen onto navigation stack.
        
        Looks up the registered screen class for the route, creates an
        instance (passing kwargs to constructor), and pushes it onto the
        stack. Then triggers the on_navigate callback to build UI elements.
        
        The optional on_navigate parameter allows overriding the default
        callback for this specific navigation.
        
        Raises ValueError if route is not registered.
        """
        
    def navigate_with_transition(self, route: str, *, on_navigate: Optional[Callable] = None, **kwargs) -> bool:
        """Navigate with fade transition animation.
        
        Similar to navigate(), but if a transition manager is set and
        not already active, starts a fade transition. The actual screen
        switch is deferred until the transition completes.
        
        Stores the target screen and callback as "pending navigation"
        until complete_transition() is called.
        
        Returns True if transition was started, False if navigated
        immediately (no transition manager or already in transition).
        """
        
    def complete_transition(self) -> None:
        """Complete a pending navigation after transition finishes.
        
        Called by the App when a fade transition completes. Appends the
        pending screen to the stack and triggers the stored callback
        (either the one passed to navigate_with_transition or the default).
        
        Clears the pending navigation state after completion.
        """
        
    def back(self) -> None:
        """Pop current screen, return to previous screen in stack.
        
        If stack has only 1 screen (at root/Main Menu), does nothing.
        Otherwise removes current screen from stack, making the previous
        screen current. The App's callback then rebuilds that screen's UI.
        
        Used for Back button behavior throughout the app.
        """
        
    def switch(self, route: str, **kwargs) -> None:
        """Replace current screen without adding to history.
        
        Pops the current screen from stack before navigating to the new
        route. This means the user cannot go "back" to the replaced screen.
        
        Used for:
        - Save & Quit (replace Game Hub with Main Menu)
        - Any navigation that should not appear in back history
        """
        
    @property
    def current(self) -> Optional[BaseScreen]:
        """Get the current top-of-stack screen.
        
        Returns the screen at the top of the navigation stack, or None
        if stack is empty. This is the active screen that should be
        rendered and receive events.
        """
        
    # Modal Management
    
    def show_confirm(self, title: str, message: str, 
                     on_confirm: Callable[[], None],
                     on_cancel: Optional[Callable[[], None]] = None,
                     confirm_text: str = "Yes", 
                     cancel_text: str = "No") -> bool:
        """Show confirmation modal - blocks navigation until dismissed.
        
        Enforces one-modal-at-a-time rule. Returns True if modal shown,
        False if another modal is already active.
        """
        
    def show_error(self, title: str, message: str) -> bool:
        """Show error message modal - blocks navigation until dismissed.
        
        Returns True if modal shown, False if another modal active.
        """
        
    def dismiss_modal(self) -> None:
        """Dismiss the currently active modal (if any).
        
        Called automatically when modal buttons are pressed, or can be
        called programmatically to close modals.
        """
        
    @property
    def has_active_modal(self) -> bool:
        """Check if a modal is currently displayed.
        
        Used to block navigation and route events to modal first.
        """
        
    def handle_modal_event(self, event: Event) -> bool:
        """Process events for the active modal.
        
        Returns True if event was consumed by modal, False otherwise.
        Should be called before passing events to screens.
        """
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

### Modals

Modal dialogs overlay the current screen to capture user attention for confirmations, errors, or inspections. The Router manages all modals centrally to enforce rules and provide consistent behavior.

**Design Rule: One Modal At A Time**

Only one modal may be visible at any given moment. The Router enforces this rule by tracking a single `_active_modal` reference. If a second modal needs to open while one is active, the request is ignored.

**Router-Managed Modals:**

The Router provides methods for showing modals:
- `router.show_confirm()` - Yes/No confirmation dialogs
- `router.show_error()` - Information/error dialogs with OK button

**Implementation:**

```python
from pygame_gui.windows import UIConfirmationDialog, UIMessageWindow

class Router:
    def show_confirm(self, title: str, message: str, 
                     on_confirm: Callable[[], None],
                     on_cancel: Optional[Callable[[], None]] = None) -> bool:
        if self._active_modal is not None:
            return False  # One at a time enforced
        
        self._active_modal = UIConfirmationDialog(
            rect=Rect(60, 250, 360, 200),
            manager=self._app.ui_manager,
            window_title=title,
            message_text=message,
            action_long_name=on_confirm.__name__,
            action_short_name="OK",
            blocking=True
        )
        self._on_confirm = on_confirm
        self._on_cancel = on_cancel
        return True
        
    def handle_modal_event(self, event: Event) -> bool:
        if self._active_modal is None:
            return False
            
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if isinstance(self._active_modal, UIConfirmationDialog):
                if event.ui_element == self._active_modal.confirm_button:
                    if self._on_confirm:
                        self._on_confirm()
                else:
                    if self._on_cancel:
                        self._on_cancel()
            
            self._active_modal = None
            return True
        return False
```

**Usage in Screens:**

```python
class BookingHubScreen(BaseScreen):
    def _on_run_show_clicked(self):
        """Show confirmation modal via Router."""
        if show_cost > self._app.state.money:
            self._router.show_confirm(
                title="Confirm Run Show",
                message=f"Cost (${show_cost}) exceeds money...",
                on_confirm=self._actually_run_show
            )
```

**Event Flow:**

```
App.handle_event()
    ↓
Router.handle_modal_event()  # Check modal first
    ↓ (if modal active)
Modal processes event → Dismissed? → Invoke callbacks
    ↓ (if no modal)
Screen.handle_event()
    ↓
Screen may call router.show_confirm()
    ↓
Router blocks navigation while modal active
```

**Key Behaviors:**

1. **Centralized**: Router owns `_active_modal`, enforces one-at-a-time rule
2. **Blocked Navigation**: Router blocks `navigate()` while modal is open
3. **Auto-blocking**: pygame_gui windows block input to underlying UI
4. **Callback-based**: Screens provide callbacks for confirm/cancel actions
5. **Event Priority**: Router checks modal events before screen events
6. **Consistent Sizing**: All modals use standard centered rectangle

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
    
    # Verify: Inspect modal opened via Router
    assert app.router.has_active_modal
    
    # Click CLOSE button on modal
    app.click(app.router._active_modal.close_button)
    
    # Verify: modal closed, back to roster
    assert not app.router.has_active_modal
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
    
    # Verify: error modal displayed via Router
    assert app.router.has_active_modal
    
    # Click OK button on modal
    app.click(app.router._active_modal.dismiss_button)
    
    # Verify: still on Save Slots, modal closed
    assert app.router.current.__class__.__name__ == "SaveSlotSelectionScreen"
    assert not app.router.has_active_modal
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

## Four-Zone Layout Deep Dive

The 4-zone layout (Header → Body → Actions → Footer) is implemented using pygame_gui containers and elements. We follow a strict rule: **no custom components**. Always use pygame_gui's built-in elements or compositions thereof.

### Design Rule: No Custom Components

**Principle:** When implementing any UI pattern, first research pygame_gui's available components using context7 or documentation. Only compose existing elements; never write custom rendering or event handling.

**Rationale:**
- pygame_gui handles theming, focus, accessibility, and event propagation
- Custom components require re-implementing solved problems
- Sticking to built-ins ensures consistent behavior across the app

**Process for adding new UI patterns:**
1. Check if pygame_gui has a component that does this (UIPanel, UIButton, UIScrollingContainer, etc.)
2. If not, compose multiple built-in elements
3. Only as last resort: extend an existing class minimally

### Zone-by-Zone Implementation

#### Header Zone (50px height)

**Purpose:** Display title, contextual info (money, show number), status indicators

**Components:**
- **Container:** `UIPanel` as header background
- **Title:** `UILabel` (left-aligned, bold, 24-26px)
- **Info labels:** `UILabel` (right-aligned for money/show number)

**Layout:**
```python
header_rect = Rect(0, 0, DESIGN_WIDTH, HEADER_HEIGHT)
header_panel = UIPanel(header_rect, manager=manager)

# Title on left with ObjectID
title_rect = Rect(MARGIN, 10, 200, 30)
UILabel(
    title_rect, "WRESTLE GM",
    manager=manager, container=header_panel,
    object_id=ObjectID(class_id='@header_title')
)

# Info on right with ObjectID
money_rect = Rect(DESIGN_WIDTH - 150, 10, 140, 30)
UILabel(
    money_rect, "$10,000",
    manager=manager, container=header_panel,
    object_id=ObjectID(class_id='@body_text')
)
```

**Info Alignment Rules:**
- Title: Always left-aligned at MARGIN (8px)
- Primary info (Money): Right-aligned
- Secondary info (Show #): Right-aligned, to left of money

#### Body Zone (Flexible height, scrollable)

**Purpose:** Primary content area - scrollable lists, forms, detailed content

**Components:**
- **Container:** `UIScrollingContainer` for scrollable content
- **Content:** `UIButton`, `UILabel`, `UISelectionList`, custom panels inside the scrolling container

**Layout:**
```python
body_rect = Rect(0, HEADER_HEIGHT, DESIGN_WIDTH, BODY_HEIGHT)
body_container = UIScrollingContainer(body_rect, manager=manager)

# Add content - it scrolls automatically if larger than container
for i, wrestler in enumerate(roster):
    row_rect = Rect(MARGIN, i * 60, DESIGN_WIDTH - 2*MARGIN, 56)
    UIButton(
        row_rect, wrestler.name,
        manager=manager, container=body_container,
        object_id=ObjectID(class_id='@body_button')
    )
```

**Scrolling Behavior:**
- `UIScrollingContainer` automatically shows vertical scrollbar when content exceeds container height
- Horizontal scrolling: Avoid if possible; design for vertical scroll only
- Scroll bar theming configured in theme.py

#### Actions Zone (70px height)

**Purpose:** Primary action buttons (Confirm, Cancel, Back)

**Components:**
- **Container:** `UIPanel` as background
- **Buttons:** `UIButton` horizontally arranged

**Layout:**
```python
actions_rect = Rect(0, HEADER_HEIGHT + BODY_HEIGHT, 
                    DESIGN_WIDTH, ACTIONS_HEIGHT)
actions_panel = UIPanel(actions_rect, manager=manager)

# Center buttons horizontally
total_button_width = 3 * 120 + 2 * 20  # 3 buttons, 20px gap
start_x = (DESIGN_WIDTH - total_button_width) // 2

# Cancel button
UIButton(
    Rect(start_x, 15, 120, 40), "CANCEL",
    manager=manager, container=actions_panel,
    object_id=ObjectID(class_id='@secondary_button')
)

# Confirm button
UIButton(
    Rect(start_x + 140, 15, 120, 40), "CONFIRM",
    manager=manager, container=actions_panel,
    object_id=ObjectID(class_id='@primary_button')
)
```

**Button Overflow Rule:**
- Maximum 3 primary action buttons visible
- If more actions needed, use "More" dropdown or move to Body zone
- Buttons are always centered horizontally in the Actions zone

#### Footer Zone (40px height)

**Purpose:** Contextual hints, status messages, keyboard shortcuts help

**Components:**
- **Container:** `UIPanel` as background
- **Text:** Single `UILabel` centered

**Layout:**
```python
footer_rect = Rect(0, DESIGN_HEIGHT - FOOTER_HEIGHT,
                   DESIGN_WIDTH, FOOTER_HEIGHT)
footer_panel = UIPanel(footer_rect, manager=manager)

hint_rect = Rect(0, 10, DESIGN_WIDTH, 20)
UILabel(
    hint_rect, "Click a wrestler to select",
    manager=manager, container=footer_panel,
    object_id=ObjectID(class_id='@footer_hint')
)
```

**Footer Content Rules:**
- Single line of text (no wrapping)
- Updated dynamically based on current context
- Center-aligned

### Complete Screen Build Example

```python
from pygame_gui.core import ObjectID

class MainMenuScreen(BaseScreen):
    def build(self, manager, rect):
        zones = self._compute_zones(rect)
        
        # HEADER - UIPanel + UILabel with ObjectID
        self._header_panel = UIPanel(zones['header'], manager=manager)
        UILabel(
            Rect(8, 10, 200, 30), "WRESTLE GM",
            manager=manager, container=self._header_panel,
            object_id=ObjectID(class_id='@header_title')
        )
        
        # BODY - UIScrollingContainer + UIButtons with ObjectIDs
        self._body_container = UIScrollingContainer(
            zones['body'], manager=manager)
        
        self._new_game_button = UIButton(
            Rect(140, 50, 200, 60), "NEW GAME",
            manager=manager, container=self._body_container,
            object_id=ObjectID(class_id='@primary_button')
        )
            
        self._load_game_button = UIButton(
            Rect(140, 130, 200, 60), "LOAD GAME",
            manager=manager, container=self._body_container,
            object_id=ObjectID(class_id='@secondary_button')
        )
            
        self._quit_button = UIButton(
            Rect(140, 210, 200, 60), "QUIT",
            manager=manager, container=self._body_container,
            object_id=ObjectID(class_id='@danger_button')
        )
        
        # ACTIONS - None for Main Menu (buttons in body)
        
        # FOOTER - UIPanel + UILabel with ObjectID
        self._footer_panel = UIPanel(zones['footer'], manager=manager)
        UILabel(
            Rect(0, 10, 480, 20), "Select an option to continue",
            manager=manager, container=self._footer_panel,
            object_id=ObjectID(class_id='@footer_hint')
        )
```

### Extensibility: Adding a New Screen

To add a new screen following the 4-zone pattern:

1. **Create screen file** in `wrestlegm/ui_pygame/screens/new_screen.py`
2. **Inherit from BaseScreen** 
3. **Implement build()** using only pygame_gui components:
   - Header: UIPanel + UILabel
   - Body: UIScrollingContainer (if scrollable) or UIPanel
   - Actions: UIPanel + UIButton (if needed)
   - Footer: UIPanel + UILabel
4. **Register in router:** `router.register("new_screen", NewScreen)`
5. **Add navigation trigger** in existing screen
6. **Add snapshot test** following the 4-zone pattern

**Example New Screen Template:**
```python
from pygame_gui.core import ObjectID

class NewFeatureScreen(BaseScreen):
    def build(self, manager, rect):
        zones = self._compute_zones(rect)
        
        # HEADER with ObjectID
        header = UIPanel(zones['header'], manager=manager)
        UILabel(
            Rect(8, 10, 200, 30), "NEW FEATURE",
            manager=manager, container=header,
            object_id=ObjectID(class_id='@header_title')
        )
        
        # BODY (scrollable if needed)
        body = UIScrollingContainer(zones['body'], manager=manager)
        # ... add content to body with ObjectIDs ...
        
        # ACTIONS (optional)
        if self._needs_actions:
            actions = UIPanel(zones['actions'], manager=manager)
            UIButton(
                Rect(10, 15, 120, 40), "ACTION",
                manager=manager, container=actions,
                object_id=ObjectID(class_id='@primary_button')
            )
        
        # FOOTER with ObjectID
        footer = UIPanel(zones['footer'], manager=manager)
        UILabel(
            Rect(0, 10, 480, 20), "Hint text here",
            manager=manager, container=footer,
            object_id=ObjectID(class_id='@footer_hint')
        )
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

**Input Constraints:**
- Touch/mouse only (no keyboard navigation)
- Minimum touch target: 44×44dp (constants.TOUCH_TARGET_MIN)
- pygame_gui normalizes touch and mouse automatically
- Gesture support not required (simple click-based game)

## Centralized Error Handling

**Fatal Error Pattern:**

All unhandled exceptions are caught by App and displayed via Router-managed fatal error modal. The user can only quit - no recovery.

```python
class WrestleGMApp:
    def run(self) -> None:
        try:
            while self._running:
                self._process_events()
                self._update()
                self._render()
        except Exception as e:
            self._logger.exception("Fatal error")
            self.router.show_fatal_error(e)
            # Continue running just to show modal
            while self.router.has_active_modal:
                self._process_events()
                self._render()
            # Modal dismissed - exit gracefully

class Router:
    def show_fatal_error(self, error: Exception) -> None:
        """Show fatal error modal with Quit option only."""
        if self._active_modal is not None:
            self._active_modal.kill()  # Replace existing modal
            
        self._fatal_error = error
        self._active_modal = UIConfirmationDialog(
            rect=Rect(60, 250, 360, 200),
            manager=self._app.ui_manager,
            window_title='Error',
            message_text=f"{type(error).__name__}: {str(error)}\n\nThe application will close.",
            action_long_name='Quit',
            action_short_name='Quit',
            blocking=True
        )
        self._on_confirm = self._app.quit_gracefully
```

**Error Types:**

1. **Fatal Errors** → `router.show_fatal_error()` → Quit only
   - Unhandled exceptions
   - Critical initialization failures
   
2. **Recoverable Errors** → `router.show_error()` → OK only
   - Save/load failures (user can retry)
   - Validation errors

**No Automatic Recovery:**
- Fatal errors always exit the app
- No save backup/restore mechanism
- User must restart the application

## Theming Strategy

**Current: ObjectID Preparation for Future Theming**

All UI elements use ObjectID to enable future theme.json customization:

```python
from pygame_gui.core import ObjectID

# Header title
UILabel(
    rect, "WRESTLE GM",
    manager=manager,
    container=header_panel,
    object_id=ObjectID(class_id='@header_title')
)

# Body text
UILabel(
    rect, "Select an option",
    manager=manager,
    container=body_container,
    object_id=ObjectID(class_id='@body_text')
)

# Primary action button
UIButton(
    rect, "CONFIRM",
    manager=manager,
    container=actions_panel,
    object_id=ObjectID(class_id='@primary_button')
)

# Secondary action button  
UIButton(
    rect, "CANCEL",
    manager=manager,
    container=actions_panel,
    object_id=ObjectID(class_id='@secondary_button')
)

# Danger button
UIButton(
    rect, "DELETE",
    manager=manager,
    container=actions_panel,
    object_id=ObjectID(class_id='@danger_button')
)
```

**ObjectID Hierarchy (Future theme.json targets):**

```
theme.json (future)
├── @header_title          (screen headers)
├── @body_text             (content text)
├── @footer_hint           (hint text)
├── @primary_button        (confirm/actions)
├── @secondary_button      (cancel/back)
├── @danger_button         (destructive actions)
├── @window_title          (modal titles)
└── @error_message         (error text)
```

**No Hardcoded Styling:**

- No inline colors, fonts, or sizes
- All styling via ObjectID + future theme.json
- Currently uses pygame_gui defaults
- Migration path: Add ObjectIDs now → Create theme.json later

**Example Screen with ObjectIDs:**

```python
class MainMenuScreen(BaseScreen):
    def build(self, manager, rect):
        zones = self._compute_zones(rect)
        
        # HEADER
        header = UIPanel(zones['header'], manager=manager)
        UILabel(
            Rect(8, 10, 200, 30), "WRESTLE GM",
            manager=manager, container=header,
            object_id=ObjectID(class_id='@header_title')
        )
        
        # BODY
        body = UIScrollingContainer(zones['body'], manager=manager)
        self._new_game_button = UIButton(
            Rect(140, 50, 200, 60), "NEW GAME",
            manager=manager, container=body,
            object_id=ObjectID(class_id='@primary_button')
        )
        
        # FOOTER
        footer = UIPanel(zones['footer'], manager=manager)
        UILabel(
            Rect(0, 10, 480, 20), "Select an option to continue",
            manager=manager, container=footer,
            object_id=ObjectID(class_id='@footer_hint')
        )
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
