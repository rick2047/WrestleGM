# Project Context

## Purpose
Create a fun wrestling manager sim where the core enjoyment comes from managing a roster, booking matches, and producing great shows over time.

## Vision & Goals
- Show-driven progression: book, simulate, and advance one show at a time.
- Deterministic but expressive outcomes driven by roster stats and match types.
- Long-term roster evolution is the core reward loop.
- Keyboard-only experience suitable for narrow terminals (target <= 40 columns).
- Systemic, not scripted: outcomes are explained by numbers, not hidden scripts.

Success criterion:
- After multiple shows, the roster and show quality clearly change based on booking decisions.

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

### Design Principles
- Show-first design with explicit show boundaries
- Textual-first UI with consistent widget and CSS usage
- Data-driven domain definitions
- Deterministic simulation (same inputs + seed = same results)
- Keyboard-only navigation and no mouse assumptions
- Explicit systems (no hidden scripts or unexplained outcomes)
- Extensible systems with no hardcoded content in the MVP

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
