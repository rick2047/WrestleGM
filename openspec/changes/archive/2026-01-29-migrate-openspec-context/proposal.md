## Why

The OpenSpec workflow now expects project context in `openspec/config.yaml`, making `openspec/project.md` redundant and prone to drift. Consolidating the context improves consistency and keeps artifact generation aligned with the new workflow.

## What Changes

- Move all project context from `openspec/project.md` into `openspec/config.yaml` under `context`.
- Update PRD inputs (`prd.md`, `make_prd.sh`) to reference the new context source.
- Add a short OpenSpec usage section to `README.md`.
- Remove `openspec/project.md` from the repo.

## Capabilities

### New Capabilities
- `project-context-in-config`: OpenSpec context lives in a single, canonical source for artifact generation.
- `openspec-quickstart-docs`: README documents how to use OpenSpec in this repo.

### Modified Capabilities
- `prd-assembly`: PRD generation now uses `openspec/config.yaml` instead of `openspec/project.md`.

## Impact

- `openspec/config.yaml`: add comprehensive project context
- `openspec/project.md`: remove
- `make_prd.sh`: update inputs
- `prd.md`: update header/source reference
- `README.md`: add OpenSpec usage section
