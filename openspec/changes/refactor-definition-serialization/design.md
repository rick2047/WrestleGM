## Context
The data layer currently relies on `*Definition` dataclasses for loading static data from JSON. These are largely duplicate shapes of the core model classes, and serialization uses ad-hoc constructor calls instead of dataclass utilities.

## Goals / Non-Goals
- Goals:
  - Remove `*Definition` dataclasses and use a single set of model classes for static data.
  - Standardize serialization/deserialization on `dataclasses.asdict` and `from_dict`/`to_dict` helpers.
  - Keep data loading deterministic and explicit; do not add new dependencies.
- Non-Goals:
  - Changing the JSON schema of `data/wrestlers.json` or `data/match_types.json`.
  - Introducing third-party serialization libraries.

## Decisions
- Decision: Replace `WrestlerDefinition`, `MatchTypeDefinition`, and `MatchCategoryDefinition` with core model dataclasses (e.g., `Wrestler`, `MatchType`, `MatchCategory`) and add `from_dict`/`to_dict` helpers.
- Decision: Use standard `dataclasses.asdict` for serialization and explicit helper constructors for nested structures (e.g., match type modifiers).

## Alternatives considered
- Keep `*Definition` classes and add `from_dict` methods to them. Rejected to reduce duplication and simplify the model surface.
- Use a third-party serializer (e.g., marshmallow-recipe). Rejected to keep dependencies minimal.

## Risks / Trade-offs
- Potential refactor churn in call sites that assume `*Definition` names. Mitigation: keep type names stable in public APIs via clear replacements and update tests.

## Migration Plan
1. Introduce replacement model dataclasses and helper methods.
2. Update data loaders and GameState/session initialization to use the new models.
3. Update tests and any documentation references.

## Open Questions
- None.
