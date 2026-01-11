# documentation Specification

## Purpose
TBD - created by archiving change add-docs-site. Update Purpose after archive.
## Requirements
### Requirement: Documentation site structure
The documentation site SHALL provide dedicated pages for architecture, simulation, UI flows, and implementation reference.

#### Scenario: Navigate core documentation
- **WHEN** the user opens the documentation site
- **THEN** they can access pages for architecture, simulation, UI, and implementation reference via the navigation

### Requirement: API reference from docstrings
The documentation site SHALL include an API reference generated from Python docstrings for the `wrestlegm` package.

#### Scenario: View API reference
- **WHEN** the user opens the API reference page
- **THEN** the page renders module, class, and function documentation from `wrestlegm` docstrings

### Requirement: Textual UI flow documentation
The documentation site SHALL describe the Textual UI screens, navigation flow, and component composition for each screen.

#### Scenario: Review UI flow details
- **WHEN** the user reads the UI documentation
- **THEN** they see each screen's purpose, key bindings, navigation behavior, and main Textual components

### Requirement: API reference grouped by domain
The documentation site SHALL group API reference content into domain sections for simulation, UI, data/state, and constants/models.

#### Scenario: Browse grouped API reference
- **WHEN** the user opens the API reference
- **THEN** module documentation appears under domain section headers

### Requirement: Comprehensive public function docstrings
The codebase SHALL provide docstrings for all public functions to support API reference generation.

#### Scenario: Render function documentation
- **WHEN** the API reference is generated
- **THEN** each public function is documented by its docstring

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

### Requirement: UI testing documentation
The system SHALL document the UI testing strategy in the `docs/` site, including flow tests, snapshot tests, and how to update baselines.

#### Scenario: Document UI test strategy
- **WHEN** a contributor reads the docs
- **THEN** they can find the UI testing strategy and snapshot update steps in `docs/`

