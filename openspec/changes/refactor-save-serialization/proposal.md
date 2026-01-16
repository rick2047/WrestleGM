# Change: Refactor save serialization with dataclass snapshots

## Why
The current persistence layer manually maps GameState into dictionaries, which is brittle and easy to desync as the model evolves. A dataclass-driven snapshot reduces maintenance overhead while enabling a clearer, versioned schema for future changes.

## What Changes
- Introduce dataclass snapshot models for save payloads and use dataclasses-based serialization.
- Update save payload schema to a new version when needed, with backward-compatible loading for v1.
- Centralize serialization/deserialization logic to reduce manual field mapping and make RNG state handling explicit.

## Impact
- Affected specs: `openspec/specs/persistence/spec.md`
- Affected code: `wrestlegm/persistence.py`, `wrestlegm/state.py`, `wrestlegm/models.py` (if snapshot types live there)
