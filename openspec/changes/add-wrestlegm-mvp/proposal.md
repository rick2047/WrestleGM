# Change: Add WrestleGM textual MVP

## Why
We need a complete MVP implementation of the WrestleGM textual management game so players can book shows, run simulations, and see progression over time.

## What Changes
- Add a data-driven roster and match type catalog for the MVP.
- Implement deterministic match simulation and show progression rules.
- Implement a Textual UI for booking, simulation, and results.
- Add tests for simulation determinism, bounds, and progression rules.

## Impact
- Affected specs: `data`, `simulation`, `game-loop`, `ui`
- Affected code: new game runtime, simulation engine, data loaders, Textual screens
