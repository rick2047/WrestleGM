# Change: Migrate UI from Textual to pygame

## Why
The current Textual UI should be replaced with a pygame-based UI to unlock richer visuals and a more traditional game presentation.

## What Changes
- Replace Textual UI with a pygame-rendered game client.
- Preserve keyboard-driven navigation and existing gameplay flows.
- Introduce pygame as a UI dependency and migrate screen rendering/event handling.

## Impact
- Affected specs: ui
- Affected code: Textual UI modules, game loop integration, UI assets/rendering
