## 1. Implementation
- [ ] 1.1 Add persistence module for save/load serialization (v1 JSON format).
- [ ] 1.2 Add save slot metadata and current slot tracking in game state.
- [ ] 1.3 Add save/load orchestration in UI flow (Main Menu, Save Slot Selection, Name Slot, Overwrite modal).
- [ ] 1.4 Trigger autosave on Results Continue after show apply/recovery.
- [ ] 1.5 Add save directory handling and update `.gitignore` for `dist/`.

## 2. Validation
- [ ] 2.1 Reject load of empty slots or unsupported save versions.
- [ ] 2.2 Block empty or whitespace-only save names.

## 3. Tests
- [ ] 3.1 Save/load round-trip integrity tests.
- [ ] 3.2 RNG determinism across save/load tests.
- [ ] 3.3 UI flow test for Load Game and Save Slot Selection.
- [ ] 3.4 UI flow test for New Game overwrite and name slot.
- [ ] 3.5 Snapshot tests for Save Slot Selection and modals.
