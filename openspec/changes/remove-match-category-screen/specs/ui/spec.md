## MODIFIED Requirements
### Requirement: Navigation stack behavior
The system SHALL push and pop screens on a navigation stack, pop on Escape where allowed, and preserve in-progress booking drafts while navigating into sub-screens.

#### Scenario: Escape pops the current screen
- **WHEN** the player presses Escape on a screen with a back action
- **THEN** the current screen is popped

#### Scenario: Subscreen selection returns
- **WHEN** the player selects a wrestler
- **THEN** the selection screen is popped and control returns to the parent screen

#### Scenario: Draft state persists across subscreens
- **WHEN** the player opens wrestler selection during booking
- **THEN** the in-progress draft remains intact when returning to booking

#### Scenario: Cancel discards draft
- **WHEN** the player cancels a booking screen
- **THEN** the in-progress draft is discarded without committing changes

### Requirement: Centralized navigation routing
The system SHALL centralize screen navigation in the app layer using named routes so screens do not import each other directly.

#### Scenario: Screen transitions use the router
- **WHEN** a screen triggers navigation (e.g., Main Menu → Save Slots, Booking Hub → Match Booking)
- **THEN** the transition is performed via a named route in the app router

### Requirement: Booking hub behavior
The system SHALL show five slots in fixed order (Match 1, Promo 1, Match 2, Promo 2, Match 3), allow slot selection, show match participant names with alignment emoji, show `Category · Stipulation` for match slots, and enable Run Show only when all slots are booked.

#### Scenario: Run Show enablement
- **WHEN** any slot is empty
- **THEN** Run Show is disabled

#### Scenario: Run Show requires a valid card
- **WHEN** the show card has validation errors
- **THEN** Run Show is disabled

#### Scenario: Show category and type for matches
- **WHEN** the booking hub renders a booked match
- **THEN** it shows a `Category · Stipulation` line under the participant list

#### Scenario: Match participants display format
- **WHEN** a match slot is booked
- **THEN** the participant line uses alignment emojis and separates names with `vs`

#### Scenario: Enter opens slot editor
- **WHEN** the player selects a match slot
- **THEN** the match booking screen opens

- **WHEN** the player selects a promo slot
- **THEN** the promo booking screen opens

#### Scenario: No partial slots on the card
- **WHEN** a slot is shown as booked in the booking hub
- **THEN** it contains a fully valid match or promo

#### Scenario: Back returns to Game Hub
- **WHEN** the player selects Back on the booking hub
- **THEN** the Game Hub is shown
