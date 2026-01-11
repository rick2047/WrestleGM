# WrestleGM Documentation

Welcome to the WrestleGM documentation. These pages describe the current MVP
architecture, simulation rules, and Textual UI flow, plus an API reference
built from docstrings.

## Doc Map

- Architecture: system layout and data flow.
- Simulation: deterministic match and show rules.
- UI: screen flow and Textual component composition.
- Implementation Reference: key files, responsibilities, and constraints.
- API Reference: generated from Python docstrings.

## Build and Preview

```bash
uv run mkdocs serve
```

```bash
uv run mkdocs build
```

## Run and Test

```bash
uv run main.py
```

```bash
uv run pytest
```
