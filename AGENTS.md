
# Workflow

## GitHub & PRs
- Repo: `https://github.com/rick2047/WrestleGM` (owned by rick2047).
- Expect `gh` auth to be logged in as `rick2047`.
- Always use the `gh` tool for all GitHub interactions (PR creation, issues, comments, etc.).
- If you don't know the exact subcommand to run, try using api access.
- Always merge PRs using a merge commit (no squash merges).
- When asked to explicitly trigger a Gemini review, comment on the PR with `/gemini review`.
- Use `gh` to check PR-scoped CI runs and inspect artifacts. Example commands:
  - `gh pr view <PR_NUMBER> --json headRefName -q .headRefName`
  - `gh run list --branch <HEAD_BRANCH> --workflow "PR Tests" --limit 1`
  - `gh run view <RUN_ID> --log`
  - `gh run download <RUN_ID> -n <ARTIFACT_NAME> -D /tmp/gh-artifacts`

## OpenSpec Workflow
- OpenSpec is the primary driver for workflow: create one PR per OpenSpec change, and keep only one change active at a time.

## Review Comment Handling
- When asked to address review comments, reply on each review comment with what you did to resolve it.
- Use `gh` for all review comment replies. Example commands you can run:
  - `gh pr review <PR_NUMBER> --comment --body "Working on the comments now."`
  - `gh api -X POST repos/<OWNER>/<REPO>/pulls/<PR_NUMBER>/comments -f body="Fixed: <what changed>" -f in_reply_to=<COMMENT_ID>`

# Testing

## General
- Always run tests with `uv` (for example, `uv run pytest`).
- Prefer multiple background terminals to run tests in parallel when possible.

## UI Snapshot Testing
UI snapshot baselines live under `tests/snapshots/test_ui_snapshots/` (stored as `.svg` snapshots) and are managed by `pytest-textual-snapshot`. To update snapshots after intentional UI changes, run:

```bash
uv run pytest tests/test_ui_snapshots.py --snapshot-update
```

Only regenerate snapshots that are affected. Avoid bulk updates; use pytest filtering to target specific tests (for example, `-k <pattern>`). The snapshot plugin writes diff artifacts to the directory configured by `TEXTUAL_SNAPSHOT_TEMPDIR`.

# Running

## Tooling
- Use `uv` to run Python (e.g., `uv run python`).