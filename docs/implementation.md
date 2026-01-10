# Implementation Reference

## Code Layout

- `main.py`: application entry point.
- `wrestlegm/constants.py`: simulation tuning constants and booking limits.
- `wrestlegm/models.py`: dataclasses for wrestlers, matches, and results.
- `wrestlegm/data.py`: JSON loaders for data-driven definitions.
- `wrestlegm/sim.py`: deterministic match and show simulation pipeline.
- `wrestlegm/state.py`: state container, booking validation, and progression.
- `wrestlegm/ui.py`: Textual UI screens and navigation flow.

## Game State

`GameState` owns:

- the RNG seed and `random.Random` instance,
- the active roster of `WrestlerState` objects,
- available match types and their modifiers,
- the current show card (fixed size),
- the last simulated show results.

`GameState` is also responsible for:

- booking validation (duplicates, stamina limits, completeness),
- running shows (simulate, aggregate ratings, apply deltas),
- applying between-show recovery.

## Booking Validation

Booking validation is centralized in `GameState.validate_match` and
`GameState.validate_show`. The UI calls these before committing a slot or
running a show, which keeps the UI display logic simple and consistent.

## Simulation Ownership

`wrestlegm.sim` is UI-agnostic. It takes plain data inputs and returns
`MatchResult` objects with rating, outcome, and stat deltas. The game state
applies those deltas at the end of a show and clamps stats to 0-100.

## Data Definitions

- `data/wrestlers.json` defines roster entries with id, name, alignment,
  popularity, and stamina.
- `data/match_types.json` defines match type modifiers and descriptions.

## Tests

`tests/test_simulation.py` focuses on deterministic outcomes, rating bounds,
and stat delta correctness.
