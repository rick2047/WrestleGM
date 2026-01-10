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

## Data Flow

1. Data definitions load from `data/wrestlers.json` and `data/match_types.json`.
2. `GameState` builds roster state, match type definitions, and RNG seed.
3. UI screens read from `GameState` and write bookings through validation.
4. Simulation runs only when a show is valid, returning match results.
5. State applies deltas at show end and advances to the next show.

## Determinism

The simulation uses a single seeded RNG stored in `GameState`. Given identical
inputs (roster stats, match types, show card, and seed), match outcomes and
ratings are reproducible.

## File Structure

- `wrestlegm/`: core gameplay logic and UI.
- `data/`: data-driven definitions for wrestlers and match types.
- `tests/`: simulation tests focused on determinism and bounds.
- `docs/`: documentation site source.
