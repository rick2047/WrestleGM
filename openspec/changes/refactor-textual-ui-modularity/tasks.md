# Tasks

- [x] Create `wrestlegm/ui/` package structure with subpackages for `screens/` and `widgets/` plus helper modules.
- [x] Move `WrestleGMApp` into `wrestlegm/ui/app.py` and add `CSS_PATH` pointing at the extracted TCSS file.
- [x] Extract shared helpers (`formatting.py`, `drafts.py`) and update screen modules to import from them.
- [x] Split each screen/modal into its own module under `wrestlegm/ui/screens/`, keeping logic unchanged.
- [x] Split reusable widgets (`EdgeAwareListView`, `FilteredListView`, `EdgeAwareDataTable`, `SafeSelect`) into `wrestlegm/ui/widgets/`.
- [x] Add `wrestlegm/ui/__init__.py` and re-export all public UI classes used by `main.py` and tests.
- [x] Update `main.py` and test imports if any are still pointing at legacy paths.
- [x] Validate UI behavior with existing UI flow tests and snapshot tests.

## Validation
- `pytest tests/test_ui_flows.py`
- `pytest tests/test_ui_snapshots.py`
