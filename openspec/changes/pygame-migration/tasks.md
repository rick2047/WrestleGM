## 1. Foundation - Setup and Core Infrastructure

- [ ] 1.1 Add pygame and pygame_gui dependencies to pyproject.toml
- [ ] 1.2 Create `wrestlegm/ui_pygame/` package structure with __init__.py
- [ ] 1.3 Create constants.py with design resolution, colors, and sizes
- [ ] 1.4 Create theme.py with pygame_gui JSON theme configuration
- [ ] 1.5 Create ScalingManager class with integer scaling logic
- [ ] 1.6 Create Router class for screen navigation (push/pop/switch)
- [ ] 1.7 Create BaseScreen class with 4-zone layout (Header → Body → Actions → Footer)
- [ ] 1.8 Create TransitionManager for fade transitions between screens
- [ ] 1.9 Create WrestleGMApp class with main game loop and UIManager
- [ ] 1.10 Update main.py to launch pygame app instead of Textual
- [ ] 1.11 Create conftest.py with pytest fixtures (pygame_app, snapshot_image)
- [ ] 1.12 Add syrupy dependency for snapshot testing

## 2. Phase 2 - Core Screens (Minimum Playable)

- [ ] 2.1 Create MainMenuScreen with New Game, Load Game, Quit buttons
- [ ] 2.2 Implement MainMenuScreen navigation to Save Slots
- [ ] 2.3 Create SaveSlotSelectionScreen with slot grid display
- [ ] 2.4 Implement new game flow (empty slot → create → Game Hub)
- [ ] 2.5 Implement load game flow (occupied slot → load → Game Hub)
- [ ] 2.6 Handle corrupt save error with modal
- [ ] 2.7 Create GameHubScreen with Continue, Booking, Roster, Quit options
- [ ] 2.8 Implement GameHub navigation to Booking Hub
- [ ] 2.9 Implement Save & Quit functionality
- [ ] 2.10 Create BookingHubScreen with 5 slot display (3 matches + 2 promos)
- [ ] 2.11 Show slot summaries (empty vs booked content)
- [ ] 2.12 Display show cost and money in Booking Hub header
- [ ] 2.13 Implement slot click → Match/Promo Booking navigation

## 3. Phase 3 - Booking Flow

- [ ] 3.1 Create MatchBookingScreen with category and type selectors
- [ ] 3.2 Implement dynamic wrestler slot count based on category
- [ ] 3.3 Create WrestlerSelectionScreen with scrollable roster list
- [ ] 3.4 Display wrestler info in list (avatar, name, stats, cost, alignment)
- [ ] 3.5 Filter unavailable wrestlers (booked, low stamina)
- [ ] 3.6 Handle wrestler selection and return to MatchBooking
- [ ] 3.7 Validate duplicate wrestler prevention
- [ ] 3.8 Show rivalry indicators between selected wrestlers
- [ ] 3.9 Implement Confirm/Cancel/Clear Slot actions with modals
- [ ] 3.10 Create PromoBookingScreen with single wrestler selection
- [ ] 3.11 Create WrestlerInspectModal for detailed wrestler view

## 4. Phase 4 - Simulation and Results

- [ ] 4.1 Create SimulatingScreen with progress indicator
- [ ] 4.2 Auto-advance to Results after simulation completes
- [ ] 4.3 Create ResultsScreen with show summary display
- [ ] 4.4 Display economy info (audience, income, costs)
- [ ] 4.5 Display per-match results (winner, rating, type)
- [ ] 4.6 Display per-promo results (wrestler, rating)
- [ ] 4.7 Implement Continue button → save → Game Hub
- [ ] 4.8 Create RosterScreen with full roster inspection
- [ ] 4.9 Implement wrestler click → Inspect modal
- [ ] 4.10 Create BankruptcyScreen with restart options

## 5. Phase 5 - Polish and Assets

- [ ] 5.1 Bundle pixel font (Press Start 2P or similar)
- [ ] 5.2 Create base modals (ConfirmModal, ErrorModal)
- [ ] 5.3 Implement confirmation modal for debt warning
- [ ] 5.4 Implement error modal for save/load failures
- [ ] 5.5 Add screen transitions (fade 300ms)
- [ ] 5.6 Test all touch targets meet 44×44dp minimum
- [ ] 5.7 Verify text readability at 16px body / 24px header
- [ ] 5.8 Test integer scaling preserves pixel art
- [ ] 5.9 Verify headless testing works (SDL_VIDEODRIVER=dummy)

## 6. Phase 6 - Testing

- [ ] 6.1 Create test_router.py with unit tests for Router class
- [ ] 6.2 Create test_scaling.py with ScalingManager tests
- [ ] 6.3 Create test_main_menu.py with visual snapshot tests
- [ ] 6.4 Create test_save_slots.py with visual snapshot tests
- [ ] 6.5 Create test_game_hub.py with visual snapshot tests
- [ ] 6.6 Create test_booking_hub.py with visual snapshot tests
- [ ] 6.7 Create test_match_booking.py with visual snapshot tests
- [ ] 6.8 Create test_promo_booking.py with visual snapshot tests
- [ ] 6.9 Create test_wrestler_selection.py with visual snapshot tests
- [ ] 6.10 Create test_results.py with visual snapshot tests
- [ ] 6.11 Generate initial baseline snapshots with --snapshot-update
- [ ] 6.12 Verify all tests pass in CI with headless mode

## 7. Final Integration

- [ ] 7.1 Verify Textual UI still works (backward compatibility)
- [ ] 7.2 Test save/load compatibility between Textual and pygame
- [ ] 7.3 Run full game loop: New Game → Book → Simulate → Results → Repeat
- [ ] 7.4 Test edge cases (bankruptcy, corrupt saves, validation errors)
- [ ] 7.5 Update README.md with pygame launch instructions
- [ ] 7.6 Verify no regression in existing game logic tests
