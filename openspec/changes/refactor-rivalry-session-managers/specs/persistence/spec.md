## MODIFIED Requirements
### Requirement: Persistence ownership boundaries
Persistence orchestration SHALL be owned by a `SessionManager`, which exposes save/load and new-game operations to the UI layer. `GameState` SHALL represent in-memory state only and SHALL NOT perform file I/O. Simulation and show application layers SHALL not perform file I/O, and `ShowApplier` SHALL not perform file I/O.

#### Scenario: No persistence in show applier
- **WHEN** show deltas are applied
- **THEN** no save or load file I/O occurs in the applier

#### Scenario: UI delegates persistence to session manager
- **WHEN** the UI needs to save, load, or start a new game
- **THEN** it invokes `SessionManager` persistence operations rather than handling file I/O directly
