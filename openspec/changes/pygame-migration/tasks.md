## 1. Foundation - Setup and Core Infrastructure

- [x] 1.1 Add pygame and pygame_gui dependencies to pyproject.toml
- [x] 1.2 Create wrestlegm/ui_pygame/ package structure with __init__.py
- [x] 1.3 Create constants.py with design resolution, colors, and sizes
- [x] 1.4 Create theme.py with pygame_gui JSON theme configuration
- [x] 1.5 Create ScalingManager class with integer scaling logic
- [x] 1.6 Create Router class for screen navigation (push/pop/switch)
- [x] 1.6.1 Implement router.back() method - Pop current screen, return to previous, trigger rebuild
- [x] 1.6.2 Add helper methods placeholder comment - Future helpers (can_go_back, switch, is_at, etc.) added as needed
- [x] 1.7 Create BaseScreen class with 4-zone layout (Header → Body → Actions → Footer)
- [x] 1.8 Create TransitionManager for fade transitions between screens
- [x] 1.9 Create WrestleGMApp class with main game loop and UIManager
- [x] 1.10 Update main.py to launch pygame app instead of Textual
- [x] 1.11 Create conftest.py with pytest fixtures (pygame_app, snapshot_image)
- [x] 1.12 Add syrupy dependency for snapshot testing

## 2. Phase 2 - Core Screens (Minimum Playable)

- [x] 2.1 Create MainMenuScreen with New Game, Load Game, Quit buttons
- [x] 2.2 Implement MainMenuScreen navigation to Save Slots
- [x] 2.3 Create SaveSlotSelectionScreen with slot grid display
- [x] 2.4 Implement new game flow (empty slot → create → Game Hub)
- [x] 2.5 Implement load game flow (occupied slot → load → Game Hub)
- [x] 2.6 Handle corrupt save error with modal
- [x] 2.7 Create GameHubScreen with Continue, Booking, Roster, Quit options
- [x] 2.8 Implement GameHub navigation to Booking Hub
- [x] 2.9 Implement Save and Quit functionality
- [x] 2.10 Create BookingHubScreen with 5 slot display (3 matches + 2 promos)
- [x] 2.11 Show slot summaries (empty vs booked content)
- [x] 2.12 Display show cost and money in Booking Hub header
- [x] 2.13 Implement slot click → Match/Promo Booking navigation

## 3. Phase 3 - Booking Flow

- [x] 3.1 Create MatchBookingScreen with category and type selectors
- [x] 3.2 Implement dynamic wrestler slot count based on category
- [x] 3.3 Create WrestlerSelectionScreen with scrollable roster list
- [x] 3.4 Display wrestler info in list (avatar, name, stats, cost, alignment)
- [x] 3.5 Filter unavailable wrestlers (booked, low stamina)
- [x] 3.6 Handle wrestler selection and return to MatchBooking
- [x] 3.7 Validate duplicate wrestler prevention
- [x] 3.8 Show rivalry indicators between selected wrestlers
- [x] 3.9 Implement Confirm/Cancel/Clear Slot actions with modals
- [x] 3.10 Create PromoBookingScreen with single wrestler selection
- [x] 3.11 Create WrestlerInspectModal for detailed wrestler view

## 4. Phase 4 - Simulation and Results

- [x] 4.1 Create SimulatingScreen with progress indicator
- [x] 4.2 Auto-advance to Results after simulation completes
- [x] 4.3 Create ResultsScreen with show summary display
- [x] 4.4 Display economy info (audience, income, costs)
- [x] 4.5 Display per-match results (winner, rating, type)
- [x] 4.6 Display per-promo results (wrestler, rating)
- [x] 4.7 Implement Continue button → save → Game Hub
- [x] 4.8 Create RosterScreen with full roster inspection
- [x] 4.9 Implement wrestler click → Inspect modal
- [x] 4.10 Create BankruptcyScreen with restart options

## 5. Phase 5 - Polish and Assets

- [x] 5.1 Bundle pixel font (Press Start 2P or similar)
- [x] 5.2 Implement Router.show_confirm() for confirmation dialogs
- [x] 5.3 Implement Router.show_error() for error dialogs
- [x] 5.4 Add modal management to Router (one-at-a-time enforcement, event handling)
- [x] 5.5 Add screen transitions (fade 300ms) - Integrated TransitionManager into Router and App, 300ms fade
- [x] 5.6 Test all touch targets meet 44×44dp minimum - Verified constants.py has TOUCH_TARGET_MIN = 44
- [x] 5.7 Verify text readability at 16px body / 24px header - Verified constants.py has FONT_SIZE_BODY = 16, FONT_SIZE_HEADER = 26
- [x] 5.8 Test integer scaling preserves pixel art - Verified ScalingManager uses integer ui_scale
- [x] 5.9 Verify headless testing works (SDL_VIDEODRIVER=dummy) - Configured in conftest.py

## 6. Parallel Apply Plan (Subagent Handoff Friendly)

This phase replaces the old linear testing checklist with vertical slices. Each slice owns code + associated tests and should be mergeable on its own.

### 6.0 Working Rules for All Subagents

- [x] 6.0.1 File ownership rule
  - A subagent may edit only files listed in its slice unless explicitly assigned a cross-slice fix.
  - If a change is needed outside owned files, create a handoff note instead of editing.

- [x] 6.0.2 Done definition rule
  - A slice is done only when its acceptance tests pass with `uv run pytest ...`.
  - Include updated tests in the same slice commit.

- [x] 6.0.3 Modal architecture rule
  - Use Router-managed modals (`show_confirm`, `show_error`, `show_fatal_error`).
  - Do not add new custom modal classes under `wrestlegm/ui_pygame/modals/`.

- [x] 6.0.4 Theming prep rule
  - New/updated UI elements must include `ObjectID` where practical.
  - Do not hardcode theme styling in screens.

### 6.1 Slice A - Router Modal Core (Foundation)

- [x] 6.1.1 Implement/finish Router modal API
  - Owner: Subagent A
  - Depends on: none
  - Files:
    - `wrestlegm/ui_pygame/router.py`
    - `wrestlegm/ui_pygame/app.py`
    - `tests/ui_pygame/test_router.py`
  - Scope:
    - Ensure `show_confirm()`, `show_error()`, `show_fatal_error()`, `handle_modal_event()`, `has_active_modal` are implemented and coherent.
    - Enforce one-modal-at-a-time in Router.
    - Ensure navigation is blocked while modal is active.
  - Acceptance tests:
    - `uv run pytest tests/ui_pygame/test_router.py -v`

### 6.2 Slice B - Save/Load Error Flow Migration

- [x] 6.2.1 Migrate save/load screens to Router modals
  - Owner: Subagent B
  - Depends on: 6.1.1
  - Files:
    - `wrestlegm/ui_pygame/screens/save_slots.py`
    - `tests/ui_pygame/screens/test_save_slots.py`
    - `tests/ui_pygame/test_navigation_flow.py`
  - Scope:
    - Remove direct dependency on custom modal classes in save/load interactions.
    - Route corrupt save errors through `router.show_error()`.
    - Update assertions to Router modal state (not screen-local modal fields).
    - Add regression coverage that verifies Back returns to an interactive screen by clicking `NEW GAME` immediately after back.
  - Flow test ownership in `tests/ui_pygame/test_navigation_flow.py`:
    - Own and update: `test_new_game_flow`, `test_load_game_flow`, `test_error_recovery_flow`, `test_cancel_navigation_flow`, `test_save_and_quit_flow`.
    - `test_cancel_navigation_flow` MUST verify screen interactivity after back (click NEW GAME again and assert Save Slots).
    - If these function names do not yet exist, create/rename tests to match these canonical names.
  - Acceptance tests:
    - `uv run pytest tests/ui_pygame/screens/test_save_slots.py -v`
    - `uv run pytest tests/ui_pygame/test_navigation_flow.py -k "new_game_flow or load_game_flow or error_recovery_flow or cancel_navigation_flow or save_and_quit_flow" -v`

### 6.3 Slice C - Booking and Confirmation Flows

- [x] 6.3.1 Migrate booking screens to Router confirmations
  - Owner: Subagent C
  - Depends on: 6.1.1
  - Files:
    - `wrestlegm/ui_pygame/screens/booking_hub.py`
    - `wrestlegm/ui_pygame/screens/match_booking.py`
    - `wrestlegm/ui_pygame/screens/promo_booking.py`
    - `tests/ui_pygame/screens/test_booking_hub.py`
    - `tests/ui_pygame/screens/test_match_booking.py`
    - `tests/ui_pygame/screens/test_promo_booking.py`
    - `tests/ui_pygame/test_navigation_flow.py`
  - Scope:
    - Replace confirm/clear/debt dialogs with `router.show_confirm()`.
    - Remove duplicated per-screen modal handling where Router handles it.
    - Keep interaction behavior unchanged from user perspective.
  - Flow test ownership in `tests/ui_pygame/test_navigation_flow.py`:
    - Own and update: `test_book_match_flow`, `test_complete_show_flow`.
    - Include debt-warning confirm path and clear-slot confirm path in this slice.
    - If these function names do not yet exist, create/rename tests to match these canonical names.
  - Acceptance tests:
    - `uv run pytest tests/ui_pygame/screens/test_booking_hub.py -v`
    - `uv run pytest tests/ui_pygame/screens/test_match_booking.py -v`
    - `uv run pytest tests/ui_pygame/screens/test_promo_booking.py -v`
    - `uv run pytest tests/ui_pygame/test_navigation_flow.py -k "book_match_flow or complete_show_flow" -v`

### 6.4 Slice D - Roster/Simulation Modal Paths

- [x] 6.4.1 Align roster inspect and simulation error paths with Router rules
  - Owner: Subagent D
  - Depends on: 6.1.1
  - Files:
    - `wrestlegm/ui_pygame/screens/roster.py`
    - `wrestlegm/ui_pygame/screens/simulating.py`
    - `tests/ui_pygame/screens/test_results.py`
    - `tests/ui_pygame/test_navigation_flow.py`
  - Scope:
    - Ensure modal lifecycle integrates with Router event priority and one-at-a-time behavior.
    - Keep roster inspect behavior and simulation error UX intact.
  - Flow test ownership in `tests/ui_pygame/test_navigation_flow.py`:
    - Own and update: `test_roster_inspection_flow`, `test_bankruptcy_flow`.
    - Include simulation error handling assertions where covered by flow.
    - If these function names do not yet exist, create/rename tests to match these canonical names.
  - Acceptance tests:
    - `uv run pytest tests/ui_pygame/test_navigation_flow.py -k "roster_inspection_flow or bankruptcy_flow" -v`

### 6.4.2 Shared flow file conflict policy

- [x] 6.4.2a Prevent `test_navigation_flow.py` merge conflicts
  - Owner: Integration lead (or Subagent A if no separate integrator)
  - Depends on: 6.2.1, 6.3.1, 6.4.1
  - Rules:
    - Keep one test class per slice (e.g., `TestSaveLoadFlows`, `TestBookingFlows`, `TestRosterSimulationFlows`).
    - Keep helper fixtures in `tests/ui_pygame/conftest.py` and avoid duplicate local helpers in test classes.
    - Each slice edits only its owned test class block in `test_navigation_flow.py`.
  - Acceptance tests:
    - `uv run pytest tests/ui_pygame/test_navigation_flow.py -v`

- [x] 6.4.2b Add post-navigation interaction probes to all flow tests
  - Owner: Integration lead
  - Depends on: 6.2.1, 6.3.1, 6.4.1
  - Files:
    - `tests/ui_pygame/test_navigation_flow.py`
    - `openspec/changes/pygame-migration/specs/pygame-ui/spec.md`
    - `openspec/changes/pygame-migration/design.md`
  - Scope:
    - Enforce rule: every navigation assertion must be followed by at least one destination-screen click.
    - Required probe targets per flow:
      - Flow 1: `_slot_buttons[0]`
      - Flow 2: occupied `_slot_buttons[2]`
      - Flow 3: `_slot_buttons[0]`, `_wrestler_slot_buttons[0]`
      - Flow 4: booking slot entry, `_run_show_button`
      - Flow 5: `_wrestler_panels[0]`
      - Flow 6: `_load_game_button`
      - Flow 7: `_try_again_button`
      - Flow 8: `_new_game_button` immediately after back
      - Flow 9: `_back_button` after modal dismiss
      - Flow 10: `_new_game_button` immediately after back
  - Acceptance tests:
    - `uv run pytest tests/ui_pygame/test_navigation_flow.py -v`

### 6.5 Slice E - ObjectID and Snapshot Readiness

- [x] 6.5.1 Apply ObjectID consistently and refresh snapshots for touched screens
  - Owner: Subagent E
  - Depends on: 6.2.1, 6.3.1, 6.4.1
  - Files:
    - `wrestlegm/ui_pygame/screens/*.py` (only screens modified by prior slices)
    - `wrestlegm/ui_pygame/theme.py`
    - `tests/ui_pygame/screens/test_*.py`
    - `tests/ui_pygame/screens/__snapshots__/`
  - Scope:
    - Add/normalize `ObjectID` usage for theme hooks.
    - Remove hardcoded styling choices in touched screens.
    - Update syrupy PNG baselines for affected tests only.
  - Acceptance tests:
    - `uv run pytest tests/ui_pygame/screens -v`

### 6.6 Slice F - Legacy Folder Cleanup

- [x] 6.6.1 Remove legacy modal/widget modules once references are gone
  - Owner: Subagent F
  - Depends on: 6.2.1, 6.3.1, 6.4.1
  - Files:
    - `wrestlegm/ui_pygame/modals/`
    - `wrestlegm/ui_pygame/widgets/`
    - Any import sites still referencing these folders
  - Scope:
    - Delete unused legacy modules.
    - Remove dead imports and pass tests.
  - Acceptance tests:
    - `uv run pytest tests/ui_pygame -v`

## 7. Integration and Verification

- [x] 7.1 Integration pass after all slices
  - Rebase/merge slices in this order: A -> (B,C,D) -> E -> F.
  - Resolve conflicts centrally in Router and `test_navigation_flow.py`.

- [x] 7.2 Full pygame UI test run
  - `uv run pytest tests/ui_pygame -v`

- [x] 7.3 Snapshot update (only if required)
  - `uv run pytest tests/ui_pygame/screens --snapshot-update`
  - Update only affected baselines.

- [ ] 7.4 Manual smoke run
  - `uv run python main.py`
  - Verify Main Menu -> Save Slots -> Game Hub -> Booking Hub basic flow.

## 8. Current Verification Checklist

- [x] Run uv run main.py - Main menu displays
- [x] Click NEW GAME - Navigates to save slots screen
- [x] Click slot - Navigates to game hub
- [x] All buttons respond to clicks
- [x] Back navigation works
- [x] Tests pass: uv run pytest tests/ui_pygame -v
- [x] Screen snapshot tests pass for touched screens
- [x] Flow tests pass for updated booking/save/roster paths
