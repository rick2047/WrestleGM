# Proposal: pygame-migration

## Motivation

The current Textual-based terminal UI has served well for early development but limits the game's potential:

1. **Visual limitations**: Terminal constraints (80×24 grid, text-only, no images) prevent rich visual presentation
2. **No multimedia**: Cannot add sound effects, music, or animations that would enhance the wrestling experience
3. **Mobile targeting**: The terminal interface is unsuitable for mobile devices, which is the desired platform
4. **User experience**: Mouse/touch interaction is more intuitive than keyboard-only navigation for a management game

Moving to pygame + pygame_gui enables:
- Custom graphics, wrestler portraits, visual effects
- Sound effects for match outcomes, crowd reactions
- Smooth animations for transitions and results
- Touch-first mobile interface
- Flexible theming and visual polish

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

### Out of Scope
- Changes to game core logic (GameState, SessionManager, SimulationEngine, etc.)
- New game features (just UI migration)
- Keyboard navigation (may be added in future)
- Desktop-specific optimizations (focus is mobile-first)
- Online features or multiplayer

## Success Criteria

1. **Functional parity**: All existing Textual screens work in pygame version
2. **Mouse-only**: Entire game playable with mouse/touch only, no keyboard required
3. **Mobile-ready**: UI elements meet mobile usability standards (min 44×44dp touch targets, readable text)
4. **Entry point**: `main.py` launches pygame version instead of Textual
5. **Tests pass**: Existing tests continue to work (they test game logic, not UI)
6. **No regression**: Game data (saves) remain compatible

## Impact

### Affected Areas
- **Entry point** (`main.py`): Switch from Textual to pygame app launch
- **UI layer** (`wrestlegm/ui/` → `wrestlegm/ui_pygame/`): New implementation
- **Dependencies**: Add pygame and pygame_gui to requirements
- **Test infrastructure**: UI snapshot tests will need updates (different output format)

### Unchanged Areas
- **Game core** (`wrestlegm/state.py`, `wrestlegm/sim.py`, `wrestlegm/economy.py`, etc.): Zero changes
- **Data layer** (`wrestlegm/data.py`, `wrestlegm/persistence.py`): Zero changes
- **Models** (`wrestlegm/models.py`): Zero changes
- **Save format**: Compatible with existing saves

## Risks & Considerations

1. **Development time**: Rebuilding ~12 screens is substantial work; will proceed task-by-task
2. **pygame_gui limitations**: May need custom widgets for complex layouts (data tables, custom wrestler cards)
3. **Mobile complexity**: Responsive design for variable screen sizes adds complexity
4. **Asset creation**: Future graphics/sounds require additional effort beyond this migration
5. **Testing**: UI snapshot tests use Textual's SVG output; will need new approach for pygame
6. **Learning curve**: pygame_gui theming and layout system has its own complexity

## Implementation Approach

Phased rollout to manage complexity:

**Phase 1: Foundation** (Entry point, screen router, base classes)
**Phase 2: Core Screens** (Main Menu, Save Slots, Game Hub, Booking Hub - minimum playable)
**Phase 3: Booking Flow** (Match Booking, Promo Booking, Wrestler Selection)
**Phase 4: Results & Polish** (Simulating, Results, Roster, remaining screens)
**Phase 5: Assets & Refinement** (Sounds, animations, responsive tweaks)

Each phase will be a set of tasks in the task artifact.
