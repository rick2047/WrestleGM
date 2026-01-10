# WrestleGM

WrestleGM is a terminal-first wrestling management game where you run a promotion
one show at a time. The game focuses on booking match cards, simulating outcomes,
and watching roster stats evolve across shows.

## Product Vision

- Show-by-show progression is the core loop, not single-match outcomes.
- Systemic, deterministic simulation with data-driven wrestlers and match types.
- Keyboard-only Textual UI designed for narrow terminals.
- Long-term booking decisions matter through stamina, popularity, and match types.

For the full MVP vision and UX details, see `wrestle_gm_textual_mvp_prd.md`.

## Current State

- Textual UI with main menu, booking hub, match booking, selection screens, and
  show results.
- Fixed 3-match show card with validation (no duplicate wrestlers, stamina limits).
- Deterministic simulation pipeline: outcome, rating, and stat deltas.
- Show ratings aggregate match ratings; stats update at show end.
- Between-show stamina recovery for wrestlers who did not appear.
- Data-driven roster and match types from JSON in `data/`.

Not yet included:
- Save/load persistence.
- Multiple promotions, titles, storylines, or injuries.
- Dynamic show sizes or match weighting.

## Requirements

- Python 3.11+
- `uv` installed (dependency management and task runner)

## Dependency Management

```bash
uv sync
```

## Run

```bash
uv run main.py
```

## Tests

```bash
uv run pytest
```

## Tooling

```bash
uv run ruff check .
uv run mkdocs serve
```

## Project Structure

- `main.py`: App entry point.
- `wrestlegm/`: Game logic, UI, and simulation code.
- `data/`: Wrestler and match type definitions.
- `openspec/`: Specifications and archived change history.
