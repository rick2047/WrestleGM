## 1. Rivalry manager extraction
- [ ] 1.1 Add `RivalryManager` to own rivalry/cooldown state and logic currently in `GameState`.
- [ ] 1.2 Update `GameState` to initialize the manager and delegate rivalry queries, emoji helpers, and advancement.
- [ ] 1.3 Update persistence serialization/deserialization to read/write rivalry and cooldown state through the manager.
- [ ] 1.4 Update rivalry-related tests to target the new manager boundary.

## 2. Session manager extraction
- [ ] 2.1 Add `SessionManager` in `wrestlegm/session.py` to own slot metadata, new-game, save, load, and clear operations.
- [ ] 2.2 Update UI and entry points to use `SessionManager` for save/load flows and to replace the active `GameState` when loading.
- [ ] 2.3 Update persistence helper tests to exercise session-based save/load and slot metadata management.

## 3. Validation
- [ ] 3.1 Run unit tests covering rivalry and persistence changes.
- [ ] 3.2 Run `openspec validate refactor-rivalry-session-managers --strict`.
