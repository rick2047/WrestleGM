## MODIFIED Requirements
### Requirement: Documentation accuracy
The documentation SHALL describe the current simulation architecture, including `SimulationEngine` ownership of RNG, `ShowApplier` state mutation, and how `GameState.run_show()` coordinates the pipeline. The documentation SHALL also reflect current UI navigation behavior, booking screen composition (including Wrestler View usage), and the minimum supported viewport of 60x30.

#### Scenario: Simulation doc accuracy
- **WHEN** a reader views the simulation documentation
- **THEN** it describes the engine-based pipeline and state application flow used in the current implementation

#### Scenario: UI and implementation doc accuracy
- **WHEN** a reader views the UI or implementation documentation
- **THEN** it reflects current navigation behavior, Wrestler View composition, and booking flow behavior

#### Scenario: Minimum viewport documented
- **WHEN** a reader views the UI documentation
- **THEN** the minimum supported viewport is documented as 60x30 with the startup guard behavior
