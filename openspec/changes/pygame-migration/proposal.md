# Proposal: pygame-migration

## Motivation

The current Textual-based terminal UI has served well for early development but limits the game's potential:

1. **Visual limitations**: Terminal constraints (80×24 grid, text-only, no images) prevent rich visual presentation
2. **No multimedia**: Cannot add sound effects, music, or animations that would enhance the wrestling experience
3. **Mobile targeting**: The terminal interface is unsuitable for mobile devices, which is the desired platform
4. **User experience**: Mouse/touch interaction is more intuitive than keyboard-only navigation for a management game

Moving to pygame + pygame_gui enables:
- Custom graphics, wrestler portraits, visual effects
- Smooth animations for transitions and results
- Touch-first mobile interface
- Flexible theming and visual polish
- **Future**: Sound effects, music (infrastructure-ready but not implemented)
- **Future**: Mobile packaging for Android/iOS (architecture supports it)

## Scope

### In Scope
- Complete replacement of Textual UI with pygame GUI
- All existing screens migrated:
  - Main Menu (New Game, Load Game, Quit)
  - Save Slot Selection
  - Game Hub (Continue, Booking, Roster, Quit)
  - Booking Hub (show card overview)
  - Match Booking (wrestler selection, match type, category)
  - Promo Booking (single wrestler selection)
  - Wrestler Selection (roster browser)
  - Roster View (full roster inspection)
  - Simulating (progress indication)
  - Results (match outcomes and ratings)
  - Bankruptcy screen
  - Modals (confirmations, error messages)
- Mouse/touch-only interaction (no keyboard shortcuts initially)
- Mobile-friendly layouts (touch targets, scrolling, readable text)
- New package structure: `wrestlegm/ui_pygame/`
- **Two-tier testing strategy** (see Testing section below)

### Out of Scope
- Changes to game core logic (GameState, SessionManager, SimulationEngine, etc.)
- New game features (just UI migration)
- Keyboard navigation (may be added in future)
- Desktop-specific optimizations (focus is mobile-first)
- Online features or multiplayer
- **Sound/audio**: Infrastructure ready but no audio assets or playback
- **Mobile packaging**: APK/IPA builds (architected for it but not setting up now)

## Success Criteria

1. **Functional parity**: All existing Textual screens work in pygame version
2. **Mouse-only**: Entire game playable with mouse/touch only, no keyboard required
3. **Mobile-ready**: UI elements meet mobile usability standards (min 44×44dp touch targets, readable text)
4. **Entry point**: `main.py` launches pygame version instead of Textual
5. **Tests pass**: Existing tests continue to work (they test game logic, not UI)
6. **Visual regression testing**: Syrupy-based PNG snapshot tests for all screens
7. **Flow testing**: Real interaction tests verify all user journeys work correctly
8. **No regression**: Game data (saves) remain compatible

## Testing Strategy Overview

This migration implements a **two-tier testing approach**:

### Tier 1: Screen Snapshot Testing (Visual Regression)
**Purpose**: Ensure UI appearance remains consistent across versions
**Approach**: 
- Use Syrupy with PNGImageSnapshotExtension
- Populate screen with test data → render → capture PNG → compare to baseline
- Tests **appearance only**, not functionality
- Each screen has one snapshot test

**Example**:
```python
def test_main_menu_snapshot(app_with_built_screen, snapshot_image):
    app = app_with_built_screen
    # Capture screen surface as PNG
    surface = pygame.Surface((480, 800))
    app.ui_manager.draw_ui(surface)
    # Compare to baseline
    assert surface_to_png(surface) == snapshot_image
```

### Tier 2: Flow Testing (Real Interaction)
**Purpose**: Ensure user interactions work correctly through the full event system
**Approach**:
- Simulate real pygame events (MOUSEBUTTONDOWN/UP)
- Events flow through: `pygame.event.post()` → `UIManager.process_events()` → `Screen.handle_event()`
- Tests **functionality and navigation**, not appearance
- Each user flow has one interaction test

**Example**:
```python
def test_new_game_flow(app_with_interaction):
    app = app_with_interaction
    # Click NEW GAME button
    app.click(app.router.current._new_game_button)
    # Verify navigation occurred
    assert app.router.current.__class__.__name__ == "SaveSlotSelectionScreen"
```

**Why Two Tiers?**
- **Separation of concerns**: Visual changes don't break functional tests, and vice versa
- **Debugging**: When a test fails, you know immediately if it's a visual regression or functional bug
- **Speed**: Snapshot tests can skip event processing; flow tests skip pixel comparison
- **Coverage**: Together they ensure both "looks right" and "works right"

## Impact

### Affected Areas
- **Entry point** (`main.py`): Switch from Textual to pygame app launch
- **UI layer** (`wrestlegm/ui/` → `wrestlegm/ui_pygame/`): New implementation
- **Dependencies**: Add pygame and pygame_gui to requirements
- **Test infrastructure**: New two-tier testing approach

### Unchanged Areas
- **Game core** (`wrestlegm/state.py`, `wrestlegm/sim.py`, `wrestlegm/economy.py`, etc.): Zero changes
- **Data layer** (`wrestlegm/data.py`, `wrestlegm/persistence.py`): Zero changes
- **Models** (`wrestlegm/models.py`): Zero changes
- **Save format**: Compatible with existing saves

## UI Architecture

All screens follow the proven **Header → Body → Actions → Footer** layout from Textual:

```
┌─────────────────────────────────────────────┐
│  Header (Title · Left Info · Right Info)    │  ~40-60px
├─────────────────────────────────────────────┤
│                                             │
│                  Body                       │  Flexible
│              (Scrollable                    │
│               Content)                      │
│                                             │
├─────────────────────────────────────────────┤
│  [ Action 1 ] [ Action 2 ] [ Action 3 ]     │  ~60-80px
├─────────────────────────────────────────────┤
│  Footer (Hints/Status)                      │  ~30-40px
└─────────────────────────────────────────────┘
```

## Required Flow Tests

These end-to-end interaction tests verify complete user journeys:

### 1. New Game Flow
**Path:** Main Menu → Save Slots → Game Hub  
**Test:** Click NEW GAME → select empty slot → verify Game Hub displays  
**Validates:** Navigation, screen building, save slot creation

### 2. Load Game Flow  
**Path:** Main Menu → Save Slots → Game Hub  
**Test:** Click LOAD GAME → select occupied slot → verify loaded state  
**Validates:** Save loading, state restoration

### 3. Book a Match Flow
**Path:** Game Hub → Booking Hub → Match Booking → Wrestler Selection → Booking Hub  
**Test:** Navigate to Booking Hub → click match slot → select wrestlers → confirm  
**Validates:** Multi-step navigation, match creation

### 4. Complete Show Flow
**Path:** Game Hub → Booking Hub → [book all 5 slots] → Run Show → Results → Game Hub  
**Test:** Book complete show → run simulation → view results → continue  
**Validates:** Full game loop, simulation integration

### 5. Roster Inspection Flow
**Path:** Game Hub → Roster → Inspect Modal → Roster  
**Test:** Navigate to Roster → click wrestler → view details → close modal  
**Validates:** Modal handling, data display

### 6. Save & Quit Flow
**Path:** Game Hub → (Save & Quit) → Main Menu → Load Game  
**Test:** Make changes → save → load → verify persistence  
**Validates:** Save functionality, data integrity

### 7. Bankruptcy Flow
**Path:** [Run shows until money < 0] → Bankruptcy → Try Again → Game Hub  
**Test:** Spend until bankrupt → restart → verify fresh state  
**Validates:** Game over detection, reset

### 8. Back Navigation Flow
**Path:** Main Menu → Save Slots → (back) → Main Menu → Game Hub → (back)  
**Test:** Navigate to Save Slots → back to Main Menu → immediately click NEW GAME again → continue deep navigation and back checks  
**Validates:** Navigation stack and post-back screen interactivity (returned screen is rebuilt, not just current)

### 9. Error Recovery Flow
**Path:** Main Menu → Load Game → (click corrupt save) → Error Modal → Save Slots  
**Test:** Attempt corrupt load → error modal → dismiss → still on Save Slots  
**Validates:** Error handling, graceful failure

### 10. Cancel Navigation Flow
**Path:** Main Menu → Save Slots → (cancel/back) → Main Menu  
**Test:** Navigate to save slots → click back → verify return to main menu  
**Validates:** Back button behavior, state preservation

## Implementation Approach

Phased rollout to manage complexity:

**Phase 1: Foundation** (Entry point, screen router, base classes, testing fixtures)
**Phase 2: Core Screens** (Main Menu, Save Slots, Game Hub, Booking Hub - minimum playable)
**Phase 3: Booking Flow** (Match Booking, Promo Booking, Wrestler Selection)
**Phase 4: Results & Polish** (Simulating, Results, Roster, remaining screens)
**Phase 5: Testing** (Screen snapshot tests, flow interaction tests)

Each phase will be a set of tasks in the task artifact.

## Why Real Interaction Testing Matters

**The Problem with Mock Tests:**
Traditional unit tests mock the UI and call methods directly. This misses bugs in the event handling chain.

**Real Interaction Testing:**
We simulate actual pygame events and let them flow through the real system:
- `pygame.event.post(MOUSEBUTTONDOWN)` - Real pygame event
- `app.ui_manager.process_events(event)` - Real pygame_gui processing  
- `screen.handle_event(event)` - Real screen handling

**Benefits:**
- Catches event handling bugs (like navigation build issues)
- Tests same code paths as real users
- No "works in test, broken in production" surprises
- Slightly slower than mocks, but catches real bugs

## Display Resolution & Scaling Strategy

**Target Design Resolution**: 480×800 (portrait)
- Fits most phones (lowest common denominator)
- Aspect ratio 9:16 matches modern smartphones

**Visual Assets**: 32×32 pixel images
- Wrestler avatars, icons, match type graphics
- Integer scaling only (no blurry interpolation)

**Touch Target Minimum**: 44×44dp
- Buttons: 48dp height minimum
- Spacing: 8dp grid system

## Visual Style Guide

**Color Palette**:
- Background: Deep grays (#1a1a1a, #2d2d2d)
- Primary: Wrestling gold (#d4af37)
- Secondary: Steel blue (#4682b4)
- Success: Green (#228b22)
- Warning: Orange (#ff8c00)
- Danger: Red (#dc143c)
- Text: Off-white (#e8e8e8)

## Risks & Considerations

1. **Testing complexity**: Two-tier testing requires more test files but provides better coverage
2. **Snapshot maintenance**: Visual tests need baseline updates when UI intentionally changes
3. **Development time**: Rebuilding ~12 screens is substantial work
4. **pygame_gui limitations**: May need custom widgets for complex layouts
5. **Mobile complexity**: Responsive design for variable screen sizes
