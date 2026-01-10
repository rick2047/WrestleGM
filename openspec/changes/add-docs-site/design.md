## Context
The project uses MkDocs for documentation and needs richer content covering architecture, simulation, and UI behavior. The API reference should be generated directly from docstrings to avoid drift.

## Goals / Non-Goals
- Goals:
  - Provide clear, structured documentation for architecture, simulation rules, and Textual UI flows.
  - Generate API reference pages from Python docstrings with minimal configuration.
- Non-Goals:
  - Add new runtime features or alter game logic.
  - Introduce a complex documentation theme or build pipeline.

## Decisions
- Use MkDocs with mkdocstrings (Python handler) for API reference output.
- Split documentation into focused pages: architecture, simulation, UI, and implementation reference.
- Keep documentation scoped to current MVP behavior and constraints.

## Alternatives Considered
- Manual API reference markdown: rejected due to drift risk and higher maintenance.
- Auto-generation via external tools (Sphinx): rejected to keep tooling minimal and consistent with MkDocs.

## Risks / Trade-offs
- Docstring coverage may require incremental improvements to keep API reference usable.
- UI documentation must be updated when Textual screens change.

## Open Questions
- None.
