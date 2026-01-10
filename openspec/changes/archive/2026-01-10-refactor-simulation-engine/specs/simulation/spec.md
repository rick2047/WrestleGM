## MODIFIED Requirements
### Requirement: Deterministic match simulation pipeline
The system SHALL simulate each match using an outcome step, rating step, and stat delta step using a single seeded RNG instance owned by a `SimulationEngine`.

#### Scenario: Deterministic outcomes with same inputs
- **WHEN** the same roster stats, match type config, show card, and seed are used
- **THEN** the match winners, ratings, and deltas are identical across runs

## ADDED Requirements
### Requirement: Simulation engine ownership
The system SHALL centralize RNG ownership and simulation methods in a `SimulationEngine` class and remove the standalone functional simulation API.

#### Scenario: Simulation runs through engine
- **WHEN** a show is simulated
- **THEN** the `SimulationEngine` is used to compute outcomes, ratings, and deltas
