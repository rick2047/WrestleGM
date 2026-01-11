# Change: Migrate UI from Textual to pygame

## Why
The current Textual-based UI does not meet the goal of delivering a pygame game experience.
Migrating the UI layer to pygame allows the game to run as a graphical application while keeping the simulation core unchanged.

## What Changes
- Replace the Textual UI layer with a pygame-driven UI.
- Preserve existing navigation, booking flow, and results presentation behavior.
- Keep the simulation core UI-agnostic while changing the presentation layer.

## Impact
- Affected specs: ui
- Affected code: UI layer modules, main entrypoint, and any Textual screen implementations
