# Change: Add MkDocs Documentation Site With API Reference

## Why
The project needs usable documentation that explains architecture, simulation rules, and UI flows, plus an API reference derived from docstrings to keep implementation details discoverable and consistent. The current docs are too shallow and the API reference lacks domain grouping and full function coverage.

## What Changes
- Add a structured documentation set in `docs/` covering architecture, simulation, UI, and implementation reference.
- Expand documentation depth with screen-level responsibilities, navigation details, and component composition.
- Configure MkDocs to generate an API reference from Python docstrings using the mkdocstrings handler.
- Group the API reference by domain (simulation, UI, data/state, constants/models).
- Ensure all public functions have docstrings for API coverage.

## Impact
- Affected specs: `specs/documentation/spec.md` (new/updated capability)
- Affected code/docs: `docs/`, `mkdocs.yml`, `pyproject.toml`, `wrestlegm/` docstrings
