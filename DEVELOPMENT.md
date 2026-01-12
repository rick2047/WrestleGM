# Development

## Skills

The `update-prd` skill keeps `prd.md` aligned with current specs and implementation.

- Packaged skill: `skills/dist/update-prd.skill`
- Installed skill directory: `/home/droid/.codex/skills/update-prd/`
- Triggers: “update prd” and “sync prd”
- Notes: Use this skill to sync `prd.md` and update related references (e.g., README/docs) when the PRD filename changes.


## UI Snapshot Testing

UI snapshot baselines live under `tests/snapshots/test_ui_snapshots/` (stored as `.raw` SVG snapshots) and are managed by `pytest-textual-snapshot`. To update snapshots after intentional UI changes, run:

```bash
uv run pytest tests/test_ui_snapshots.py --snapshot-update
```

The snapshot plugin writes diff artifacts to the directory configured by `TEXTUAL_SNAPSHOT_TEMPDIR`.
