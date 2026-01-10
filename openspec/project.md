# Project Context

## Purpose
Create a fun wrestling manager sim where the core enjoyment comes from managing a roster, booking matches, and producing great shows over time.

## Tech Stack
- Python (Textual for UI)
- pytest, ruff, mkdocs
- Minimal third-party dependencies

## Project Conventions

### Code Style
- Prefer clear, Zen-of-Python style implementations
- Use docstrings on modules, classes, and public functions

### Architecture Patterns
- Modular structure with a clear separation between simulation and UI
- Simulation core should be UI-agnostic to allow future UI swaps

### Testing Strategy
- Emphasize determinism and consistency in simulation tests
- Cover bounds and regression cases for core simulation rules

### Git Workflow
- Use detailed, descriptive commit messages

## Domain Context
- The game is show-driven: book 3-match cards, simulate, apply deltas, advance

## Important Constraints
- Keep dependencies minimal
- Keep simulation and UI layers separated for future UI migration

## External Dependencies
- None for MVP
