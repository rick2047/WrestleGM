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

### Requirement: GameState is the UI economy access point
The system SHALL expose economy-related data to the UI through `GameState` accessors rather than direct economy module usage.

#### Scenario: Booking cost available via GameState
- **WHEN** the UI requests the current show cost
- **THEN** `GameState.current_show_cost()` provides that value without the UI calling economy calculation functions directly
