## 1. Rivalry manager extraction
- [x] 1.1 Add `RivalryManager` to own rivalry/cooldown state and logic currently in `GameState`.
- [x] 1.2 Update `GameState` to initialize the manager and delegate rivalry queries, emoji helpers, and advancement.
- [x] 1.3 Update persistence serialization/deserialization to read/write rivalry and cooldown state through the manager.
- [x] 1.4 Update rivalry-related tests to target the new manager boundary.

## 2. Session manager extraction
- [x] 2.1 Add `SessionManager` in `wrestlegm/session.py` to own slot metadata, new-game, save, load, and clear operations.
- [x] 2.2 Update UI and entry points to use `SessionManager` for save/load flows and to replace the active `GameState` when loading.
- [x] 2.3 Update persistence helper tests to exercise session-based save/load and slot metadata management.

## 3. Validation
- [x] 3.1 Run unit tests covering rivalry and persistence changes.
- [x] 3.2 Run `openspec validate refactor-rivalry-session-managers --strict`.
