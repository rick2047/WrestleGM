# WrestleGM

WrestleGM is a wrestling management game where you run a promotion one show at a
time. The game focuses on booking match cards, simulating outcomes, and watching
roster stats evolve across shows.

## Product Vision

- Show-by-show progression is the core loop, not single-match outcomes.
- Systemic, deterministic simulation with data-driven wrestlers and match types.
- Touch-first pygame UI designed for mobile and desktop.
- Long-term booking decisions matter through stamina, popularity, and match types.

For the full MVP vision and UX details, see `prd.md`.

## Current State

- **pygame UI** (current default): Touch-friendly interface with main menu,
  save slots, game hub, booking hub, match/promo booking, wrestler selection,
  simulating progress, and show results.
- **Textual UI** (backward compatibility): Terminal interface preserved in
  `wrestlegm/ui/` for existing users.
- Fixed 3-match show card with validation (no duplicate wrestlers, stamina limits).
- Deterministic simulation pipeline: outcome, rating, and stat deltas.
- Show ratings aggregate match ratings; stats update at show end.
- Between-show stamina recovery for wrestlers who did not appear.
- Data-driven roster and match types from JSON in `data/`.
- Save/load persistence across both UI versions.

Not yet included:
- Multiple promotions, titles, storylines, or injuries.
- Dynamic show sizes or match weighting.

## Requirements

- Python 3.11+
- `uv` installed (dependency management and task runner)
- pygame dependencies (automatically installed via `uv sync`)

## Dependency Management

```bash
uv sync
```

## Run

### pygame UI (Default - Mobile/Tablet/Desktop)

The pygame UI provides a touch-friendly interface with smooth transitions,
scrollable lists, and visual feedback. Default launch:

```bash
uv run main.py
```

### Textual UI (Legacy - Terminal)

The Textual UI is available in `wrestlegm/ui/` for backward compatibility.
To use it, modify `main.py` to import from `wrestlegm.ui` instead of
`wrestlegm.ui_pygame`.

## Tests

```bash
uv run pytest
```

For pygame UI visual snapshot tests:

```bash
# Run with headless display (CI/CD compatible)
SDL_VIDEODRIVER=dummy uv run pytest tests/ui_pygame/ -v

# Update snapshots after intentional UI changes
uv run pytest tests/ui_pygame/ --snapshot-update
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

## OpenSpec Workflow

OpenSpec artifacts live in `openspec/changes/<change-name>/` while a change is active and in `openspec/archive/` once completed.

Core commands:

```bash
openspec new change <name>
openspec continue <name>
openspec apply <name>
openspec verify <name>
openspec archive <name>
openspec status --change <name>
openspec list
```
