# Change: Treat match type rating bonus as a modifier

## Why
The PRD now frames the match type rating bonus as part of the rating modifier system, but the spec and implementation describe it as a separate step. Aligning the spec and implementation with the PRD will make the modifier flow consistent and simpler to explain.

## What Changes
- Treat the match type rating bonus as a `RatingModifier` instead of a separate step.
- Update simulation specs to describe the unified modifier flow.
- Remove `RatingDebug` from the simulation output and specs.

## Impact
- Affected specs: `specs/simulation/spec.md`
- Affected code: `wrestlegm/sim.py`, tests
