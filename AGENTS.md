
## Workflow Rules
- Always merge PRs using a merge commit (no squash merges).
- To trigger a Gemini review, comment on the PR with `/gemini review`.

## GitHub Access
- Use the GitHub MCP server for all GitHub issues/PRs/comments and related actions.
- Do not use the `gh` CLI or raw API calls.

## OpenSpec CLI Location
- Prefer running `openspec` from `PATH`.
- If `openspec` is not found on `PATH`, use the absolute path: `/home/droid/.nvm/versions/node/v24.12.0/bin/openspec`.
## Tooling
- Use `uv` to run pytest (e.g., `uv run pytest`).
- Use `uv` to run Python (e.g., `uv run python`).
- Prefer multiple background terminals to run tests in parallel when possible.
