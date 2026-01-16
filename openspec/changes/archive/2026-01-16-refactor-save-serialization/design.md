## Context
Persistence currently relies on hand-written dict assembly and parsing in `wrestlegm/persistence.py`. This is verbose, error-prone, and tightly coupled to the in-memory `GameState` layout.

## Goals / Non-Goals
- Goals:
  - Replace manual mapping with dataclass snapshot types that define the persisted schema.
  - Allow schema evolution via explicit versioning while preserving determinism and load behavior.
  - Keep JSON human-readable and minimize new dependencies.
- Non-Goals:
  - Changing gameplay rules or simulation behavior.
  - Introducing external serialization libraries.

## Decisions
- Decision: Persist using existing domain dataclasses serialized with `dataclasses.asdict`, avoiding separate snapshot classes.
- Decision: Enforce strict save version matching (`version == SAVE_VERSION`) with no backward compatibility.
- Decision: Keep RNG state persistence explicit (seed plus RNG state) with tuple/list conversion.
- Decision: Harden deserialization with defensive `.get()` access and type guards to avoid crashes on malformed payloads.
- Decision: Route load flow to the Game Hub after successful load.
- Decision: Defer load action from the slot selection to avoid Enter key propagation into the next screen.

## Alternatives considered
- Continue manual mapping with helper functions (rejected: high maintenance cost).
- Use a custom JSON encoder/decoder without snapshots (rejected: still requires manual schema definition and mapping).

## Risks / Trade-offs
- Schema versioning introduces migration logic; mitigate with explicit tests for v1 and v2 load paths.
- Dataclass snapshots may diverge from runtime objects; mitigate with centralized conversion functions and test coverage.

## Migration Plan
- Add load support for v1 and v2 payloads in persistence.
- Save in v2 format by default; keep v1 parsing until a future removal change.
- Add regression tests to confirm v1 and v2 load produce identical in-memory state.

## Open Questions
- Do we want to keep the v1 schema indefinitely or set a future deprecation window?
- Should snapshot dataclasses live in `wrestlegm/models.py` or a new `wrestlegm/persistence_models.py` module?
