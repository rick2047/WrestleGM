## ADDED Requirements

### Requirement: Stateless economy simulation
The system SHALL provide an `EconomySimulator` that computes economy outputs purely from inputs and deterministic RNG, without owning or mutating persistent economy state.

#### Scenario: Deterministic outputs from inputs
- **WHEN** `EconomySimulator.compute_show(...)` is called with the same inputs and RNG seed
- **THEN** it returns the same `show_cost`, `audience`, `gate_income`, `merch_income`, and `total_earned` values

#### Scenario: No dependence on prior calls
- **WHEN** `EconomySimulator.compute_show(...)` is called multiple times with identical inputs
- **THEN** the returned values depend only on the provided inputs and RNG, not on earlier calls

### Requirement: Economy calculations follow existing rules
The simulator SHALL implement the economy formulas and rules defined in the existing `economy` capability specification.

#### Scenario: Show economy uses existing formulas
- **WHEN** `EconomySimulator.compute_show(...)` produces economy results
- **THEN** `show_cost`, `audience`, `gate_income`, `merch_income`, and `total_earned` follow the rules in `openspec/specs/economy/spec.md`

### Requirement: GameState applies simulator results
The system SHALL have `GameState` apply economy results from the simulator to update promotion money and show outputs.

#### Scenario: Money updated from simulator results
- **WHEN** a show completes simulation
- **THEN** `GameState.money` is updated as `money = money - show_cost + gate_income + merch_income` using the simulator results

#### Scenario: Show outputs populated from simulator results
- **WHEN** a show completes simulation
- **THEN** `Show.show_cost`, `Show.audience`, `Show.gate_income`, `Show.merch_income`, and `Show.total_earned` are populated from the simulator results

### Requirement: Show slots carry wrestler state
The system SHALL store `WrestlerState` objects directly in show slots instead of wrestler IDs.

#### Scenario: Match slots contain wrestler state
- **WHEN** a match slot is stored on the show card
- **THEN** it contains a list of `WrestlerState` objects for the booked wrestlers

#### Scenario: Promo slots contain wrestler state
- **WHEN** a promo slot is stored on the show card
- **THEN** it contains a `WrestlerState` object for the booked wrestler

### Requirement: Bankruptcy is based on money only
The system SHALL treat the game as bankrupt when `GameState.money <= 0`.

#### Scenario: Bankruptcy at non-positive money
- **WHEN** `GameState.money` is `0` or negative
- **THEN** `GameState.is_bankrupt()` returns `True`

#### Scenario: Not bankrupt with positive money
- **WHEN** `GameState.money` is greater than `0`
- **THEN** `GameState.is_bankrupt()` returns `False`

### Requirement: No minimum show cost calculation
The system SHALL NOT compute a `min_valid_show_cost` for bankruptcy or booking flow checks.

#### Scenario: Bankruptcy ignores affordability checks
- **WHEN** bankruptcy status is evaluated
- **THEN** it does not consider any minimum show cost calculation

### Requirement: GameState is the UI economy access point
The system SHALL provide economy-related data to the UI exclusively through `GameState` accessors.

#### Scenario: Booking cost available via GameState
- **WHEN** the UI renders booking costs
- **THEN** it uses `GameState` accessors (e.g., `GameState.current_show_cost()` and `GameState.wrestler_booking_price(...)`) and does not call economy helpers directly
