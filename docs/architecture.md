# Architecture

## Overview
WrestleGM is a show-by-show wrestling management game with a deterministic
simulation core and a Textual UI. The architecture keeps simulation logic
UI-agnostic so the front-end can evolve without rewriting match rules.

## Layers and Responsibilities

- `wrestlegm.models`: dataclasses that define the domain vocabulary.
- `wrestlegm.data`: JSON loading for wrestlers and match types.
- `wrestlegm.sim`: deterministic match and show simulation pipeline.
- `wrestlegm.state`: in-memory game state, booking validation, and lifecycle.
- `wrestlegm.ui`: Textual screens and navigation flow.
- `main.py`: app entry point.

## Module Boundaries

- `wrestlegm.sim` accepts plain data and returns results without mutating state.
- `wrestlegm.state` owns mutation (applying deltas, advancing shows, recovery).
- `wrestlegm.ui` never computes match outcomes; it only orchestrates flow.
- `wrestlegm.data` is the only place that reads JSON from disk.

This separation keeps simulation rules portable and makes the UI a thin layer
over state transitions.

## Class Collaboration

Key classes coordinate the show loop as follows:

- `WrestleGMApp` creates `GameState` from data loaders and owns the screen stack.
- UI screens (such as `BookingHubScreen` and `ResultsScreen`) read from
  `GameState` and request transitions.
- `GameState` validates bookings and calls the simulation functions in
  `wrestlegm.sim`.
- Simulation functions return `MatchResult` data without mutating state.
- `GameState` applies deltas and updates the roster after the show completes.

## Class Diagram (Conceptual)

```text
WrestleGMApp
  |
  v
GameState <-----------------------------+
  |                                     |
  | uses                                | reads/writes
  v                                     |
Simulation (simulate_* functions)       |
  |                                     |
  v                                     |
MatchResult ----------------------------+

UI Screens (MainMenu, BookingHub, MatchBooking, Results)
  |
  v
GameState (validate, run_show, apply_show_results)
```

## Data Flow

1. Data definitions load from `data/wrestlers.json` and `data/match_types.json`.
2. `GameState` builds roster state, match type definitions, and RNG seed.
3. UI screens read from `GameState` and write bookings through validation.
4. Simulation runs only when a show is valid, returning match results.
5. State applies deltas at show end and advances to the next show.

## Show Lifecycle

- Planning: the booking hub displays the current card and allows edits.
- Locked: a show is implicitly locked once all slots are booked and Run Show is
  triggered.
- Simulating: `GameState.run_show()` calls the simulation pipeline in card
  order.
- Completed: results are stored on `GameState.last_show` for the results screen.
- Applied: deltas and recovery are applied, the show index increments, and the
  card resets for the next show.

## Validation Flow

- Slot-level validation runs in `GameState.validate_match`.
- Show-level validation runs in `GameState.validate_show`.
- The UI disables actions when validation fails and refuses invalid selections.

## Determinism

The simulation uses a single seeded RNG stored in `GameState`. Given identical
inputs (roster stats, match types, show card, and seed), match outcomes and
ratings are reproducible.

## State Mutation Rules

- All stat changes are applied at show end, not per match.
- Recovery is applied only to wrestlers who did not participate in the show.
- Popularity and stamina always clamp to 0-100 after application.

## File Structure

- `wrestlegm/`: core gameplay logic and UI.
- `data/`: data-driven definitions for wrestlers and match types.
- `tests/`: simulation tests focused on determinism and bounds.
- `docs/`: documentation site source.
