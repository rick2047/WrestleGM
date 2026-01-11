## ADDED Requirements
### Requirement: Documentation accuracy
The documentation SHALL describe the current simulation architecture, including `SimulationEngine` ownership of RNG, `ShowApplier` state mutation, and how `GameState.run_show()` coordinates the pipeline. The documentation SHALL also reflect current UI navigation behavior, implementation ownership details, and command-line usage for running the app, tests, and docs.

#### Scenario: Simulation doc accuracy
- **WHEN** a reader views the simulation documentation
- **THEN** it describes the engine-based pipeline and state application flow used in the current implementation

#### Scenario: UI and implementation doc accuracy
- **WHEN** a reader views the UI or implementation documentation
- **THEN** it reflects current navigation behavior, component focus rules, and ownership boundaries

#### Scenario: Command-line usage accuracy
- **WHEN** a reader views the documentation index
- **THEN** it lists `uv` commands for running the app, tests, and docs
