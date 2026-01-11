## MODIFIED Requirements
### Requirement: Documentation completeness
The documentation SHALL describe the current simulation architecture, including `SimulationEngine` ownership of RNG, `ShowApplier` state mutation, and how `GameState.run_show()` coordinates the pipeline.

#### Scenario: Simulation doc accuracy
- **WHEN** a reader views the simulation documentation
- **THEN** it describes the engine-based pipeline and state application flow used in the current implementation
