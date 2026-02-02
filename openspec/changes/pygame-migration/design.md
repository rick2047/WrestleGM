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

## Open Questions

1. **Font**: Bundle a pixel font (e.g., [Press Start 2P](https://fonts.google.com/specimen/Press+Start+2P) or similar open source pixel font)
2. **Image formats**: PNG for pixel art with transparency
3. **Mobile packaging**: buildozer for Android APK?
