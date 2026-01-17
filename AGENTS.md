<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

## Workflow Rules
- Always merge PRs using a merge commit (no squash merges).
- When you create a PR for the first time, automatically trigger a Gemini review (no extra prompt needed).

## GitHub Access
- Use the GitHub MCP server for all GitHub issues/PRs/comments and related actions.
- Do not use the `gh` CLI or raw API calls.

## OpenSpec CLI Location
- Prefer running `openspec` from `PATH`.
- If `openspec` is not found on `PATH`, use the absolute path: `/home/droid/.nvm/versions/node/v24.12.0/bin/openspec`.
