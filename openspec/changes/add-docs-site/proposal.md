# Change: Add MkDocs Documentation Site With API Reference

## Why
The project needs usable documentation that explains architecture, simulation rules, and UI flows, plus an API reference derived from docstrings to keep implementation details discoverable and consistent.

## What Changes
- Add a structured documentation set in `docs/` covering architecture, simulation, UI, and implementation reference.
- Configure MkDocs to generate an API reference from Python docstrings using the mkdocstrings handler.
- Document Textual UI flows and component composition in the UI documentation section.

## Impact
- Affected specs: `specs/documentation/spec.md` (new capability)
- Affected code/docs: `docs/`, `mkdocs.yml`, `pyproject.toml`, `wrestlegm/` docstrings (as needed)
