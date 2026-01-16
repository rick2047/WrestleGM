## ADDED Requirements
### Requirement: Rivalry state ownership via RivalryManager
The system SHALL encapsulate rivalry and cooldown state plus progression logic within a dedicated `RivalryManager` owned by `GameState`, and `GameState` SHALL delegate rivalry queries and advancement to this manager.

#### Scenario: Game state delegates rivalry work
- **WHEN** the game advances a show or queries rivalry/cooldown values
- **THEN** the `RivalryManager` is responsible for the rivalry and cooldown state transitions and lookups
