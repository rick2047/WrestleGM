# Development

## Skills

The `update-prd` skill keeps `prd.md` aligned with current specs and implementation.

- Packaged skill: `skills/dist/update-prd.skill`
- Installed skill directory: `/home/droid/.codex/skills/update-prd/`
- Triggers: “update prd” and “sync prd”
- Notes: Use this skill to sync `prd.md` and update related references (e.g., README/docs) when the PRD filename changes.

## GitHub Access

Use the `gh` CLI for GitHub issues/PRs/comments rather than raw API calls. Assume authentication is already configured and do not prompt for login.

## UI Snapshot Testing

UI snapshot baselines live under `tests/snapshots/`. To update snapshots after intentional UI changes, run:

```bash
uv run pytest tests/test_ui_snapshots.py --snapshot-update
```

Failed snapshot outputs are written to `tests/snapshots/__failed__/` for review.
