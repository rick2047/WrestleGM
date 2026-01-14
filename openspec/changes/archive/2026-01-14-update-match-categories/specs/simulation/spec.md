## MODIFIED Requirements
### Requirement: Deterministic match simulation pipeline
The system SHALL simulate each match using an outcome step, rating step, and stat delta step using a single seeded RNG instance owned by a `SimulationEngine`, and SHALL support matches with `N` wrestlers where `N >= 2`.

#### Scenario: Deterministic outcomes with same inputs
- **WHEN** the same roster stats, stipulation config, show card, and seed are used for matches with `N >= 2`
- **THEN** the match winners, ratings, and deltas are identical across runs
