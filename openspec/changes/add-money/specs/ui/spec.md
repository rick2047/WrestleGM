## ADDED Requirements

### Requirement: Booking hub economy display
The system SHALL display current money, total show cost, and rivalry/cooldown counts on the Booking Hub.

#### Scenario: Booking hub header economy line
- **WHEN** the Booking Hub is rendered
- **THEN** it shows current money and total show cost in the header line
- **AND THEN** negative money is rendered in red

#### Scenario: Booking hub rivalry/cooldown badges
- **WHEN** the Booking Hub is rendered
- **THEN** it shows rivalry and cooldown counts for the current card in the header badges

#### Scenario: Match slot cost label
- **WHEN** a match slot is rendered
- **THEN** its title includes the total cost for the slot (match type base cost + booked wrestler costs) (e.g., `Match 1 · Singles · $2,450`)

#### Scenario: Promo slot cost label
- **WHEN** a promo slot is rendered
- **THEN** its title includes the booked wrestler cost (e.g., `Promo 1 · $220`)

### Requirement: Run show confirmation warning
The system SHALL present a confirmation modal before running a show and warn if it will result in debt.

#### Scenario: Confirm run show modal
- **WHEN** the player activates Run Show
- **THEN** a modal with Confirm/Cancel actions is shown with trapped focus

#### Scenario: Debt warning in modal
- **WHEN** the show cost exceeds current money
- **THEN** the modal displays `WARNING: This will put you into debt.`

#### Scenario: No after-show estimate
- **WHEN** the confirm modal is shown
- **THEN** the After Show field displays `$—` and no estimate is provided

### Requirement: Results economy breakdown
The system SHALL display audience, gate income, merch income, total earned, and current money on the Results screen.

#### Scenario: Results economy fields
- **WHEN** the Results screen is shown
- **THEN** it displays audience, gate income, merch income, total earned, and current money

### Requirement: Bankruptcy game over screen
The system SHALL present a Game Over: Bankruptcy screen when the player cannot afford any valid next show.

#### Scenario: Bankruptcy screen layout
- **WHEN** bankruptcy is triggered
- **THEN** the screen shows the final money value and offers a single action to return to Main Menu
