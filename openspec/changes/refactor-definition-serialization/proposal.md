# Change: Refactor model definition serialization

## Why
The current `*Definition` dataclasses duplicate core model structures and force bespoke JSON handling. Using standard dataclass serialization helpers will reduce redundant types while keeping data loading explicit and predictable.

## What Changes
- Remove `WrestlerDefinition`, `MatchTypeDefinition`, and `MatchCategoryDefinition` in favor of core model dataclasses with `from_dict`/`to_dict` helpers.
- Update data loading and any affected call sites to use the shared model classes and standard dataclass serialization (`dataclasses.asdict`).
- Update tests and documentation to reflect the new model/serialization approach.

## Impact
- Affected specs: `specs/data/spec.md`
- Affected code: `wrestlegm/models.py`, `wrestlegm/data.py`, `wrestlegm/state.py`, `wrestlegm/session.py`, tests
