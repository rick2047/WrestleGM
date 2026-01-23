## ADDED Requirements

### Requirement: Modular UI organization
The UI implementation SHALL be organized into a package that separates the app entry point, screen modules, reusable widgets, and shared formatting helpers.

#### Scenario: Screen modules are isolated
- **WHEN** a developer opens a specific screen implementation
- **THEN** the screen logic lives in a dedicated module under `wrestlegm/ui/screens/`

#### Scenario: Widgets are reusable and screen-agnostic
- **WHEN** a custom widget is shared across multiple screens
- **THEN** it lives under `wrestlegm/ui/widgets/` and does not depend on game-state globals

#### Scenario: Stable public imports
- **WHEN** external code imports `WrestleGMApp` or screen classes from `wrestlegm.ui`
- **THEN** those imports remain valid via package re-exports

### Requirement: Externalized UI styling
The Textual app SHALL load its CSS from a `.tcss` file to keep styling separate from screen logic.

#### Scenario: CSS path configuration
- **WHEN** the app starts
- **THEN** `WrestleGMApp` loads styling via `CSS_PATH` pointing at the UI stylesheet
