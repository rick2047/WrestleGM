## 1. Implementation
- [x] 1.1 Add persistence module for save/load serialization (v1 JSON format).
- [x] 1.2 Add save slot metadata and current slot tracking in game state.
- [x] 1.3 Add save/load orchestration in UI flow (Main Menu, Save Slot Selection, Name Slot, Overwrite modal).
- [x] 1.4 Trigger autosave on Results Continue after show apply/recovery.
- [x] 1.5 Add save directory handling and update `.gitignore` for `dist/`.

## 2. Validation
- [x] 2.1 Reject load of empty slots or unsupported save versions.
- [x] 2.2 Block empty or whitespace-only save names.

## 3. Tests
- [x] 3.1 Save/load round-trip integrity tests.
- [x] 3.2 RNG determinism across save/load tests.
- [x] 3.3 UI flow test for Load Game and Save Slot Selection.
- [x] 3.4 UI flow test for New Game overwrite and name slot.
- [x] 3.5 Snapshot tests for Save Slot Selection and modals.
