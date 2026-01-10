## ADDED Requirements
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
