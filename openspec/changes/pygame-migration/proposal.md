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
6. **Visual snapshot testing**: New pygame UI has Syrupy-based PNG snapshot tests matching Textual coverage
7. **No regression**: Game data (saves) remain compatible

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

- **Header**: Dynamic title, contextual info (money, show number), status indicators
- **Body**: Primary content, scrollable when needed, touch-friendly spacing
- **Actions**: Primary action buttons (Confirm, Cancel, Back), disabled state support
- **Footer**: Contextual hints or status messages

This consistency reduces cognitive load and mirrors the terminal UI users already know.

## Display Resolution & Scaling Strategy

**Target Design Resolution**: 480×800 (portrait)
- Fits most phones (lowest common denominator)
- Aspect ratio 9:16 matches modern smartphones
- Desktop windowed mode scales proportionally

**Visual Assets**: 32×32 pixel images
- Wrestler avatars, icons, match type graphics
- Crisp at 1× scale, acceptable at 2× (64×64)
- Integer scaling only (no blurry interpolation)

**Text Strategy**:
| Element | Size | Notes |
|---------|------|-------|
| Header Title | 24-28px | Bold, primary |
| Body Text | 16-18px | Readable at arm's length |
| Stats/Numbers | 20-24px | Important values stand out |
| Buttons | 18-20px | Clear call-to-action |
| Footer | 14-16px | Secondary information |

**Touch Target Minimum**: 44×44dp (density-independent pixels)
- Buttons: 48dp height minimum
- List items: 56-64dp for easy selection
- Spacing: 8dp grid system (margins, padding)

**Scaling Approach**:
- Design at 1× (480×800)
- Runtime scale to device: `scale = min(width/480, height/800)`
- UI elements scale linearly, pixel art stays crisp at integer multiples
- Letterbox if aspect ratio differs (maintain game area aspect)

**Implications of 32×32 Pixel Art**:
- **Pro**: Small download size, retro aesthetic, fast to create
- **Con**: Limited detail for wrestler expressions, scales poorly to tablets
- **Mitigation**: Focus on readable text and color coding; pixel art supplements rather than communicates primary info

## Visual Style Guide

**Color Palette** (retro-inspired but readable):
- Background: Deep grays (#1a1a1a, #2d2d2d)
- Primary: Wrestling gold (#d4af37) for headers, important actions
- Secondary: Steel blue (#4682b4) for secondary info
- Success: Green (#228b22) for positive outcomes
- Warning: Orange (#ff8c00) for stamina warnings
- Danger: Red (#dc143c) for errors, bankruptcy
- Text: Off-white (#e8e8e8) for readability

**Typography**:
- Use system fonts or bundled pixel font
- All caps for headers (terminates better at low res)
- Monospace for stats/tables (alignment)
- Emoji support for alignment icons, rivalry indicators

## Implementation Approach

Phased rollout to manage complexity:

**Phase 1: Foundation** (Entry point, screen router, base classes)
**Phase 2: Core Screens** (Main Menu, Save Slots, Game Hub, Booking Hub - minimum playable)
**Phase 3: Booking Flow** (Match Booking, Promo Booking, Wrestler Selection)
**Phase 4: Results & Polish** (Simulating, Results, Roster, remaining screens)
**Phase 5: Assets & Refinement** (Sounds, animations, responsive tweaks)

Each phase will be a set of tasks in the task artifact.
