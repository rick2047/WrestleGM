# Change: Refactor rivalry and session management

## Why
`GameState` currently owns rivalry progression and persistence orchestration, which makes it a god object and blurs boundaries between simulation state and storage. Extracting these responsibilities improves modularity, testability, and future extensibility without changing player-facing behavior.

## What Changes
- Introduce a `RivalryManager` that owns rivalry/cooldown state and logic, with `GameState` delegating queries and progression.
- Introduce a `SessionManager` (in `wrestlegm/session.py`) that owns save/load/slot operations and related slot metadata state.
- Update persistence ownership boundaries to reflect the new session layer.

## Impact
- Affected specs: `openspec/specs/rivalry/spec.md`, `openspec/specs/persistence/spec.md`
- Affected code: `wrestlegm/state.py`, `wrestlegm/persistence.py`, new `wrestlegm/rivalries.py`, new `wrestlegm/session.py`, UI entry points that call save/load
