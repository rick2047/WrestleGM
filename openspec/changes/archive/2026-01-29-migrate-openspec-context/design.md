## Context

The project currently stores OpenSpec context in `openspec/project.md`, while the newer OpenSpec workflow expects context in `openspec/config.yaml`. The PRD assembly script and PRD header still reference the old file. We need to consolidate context and remove the redundant file without losing any guidance for artifacts.

## Goals / Non-Goals

**Goals:**
- Consolidate all OpenSpec project context into `openspec/config.yaml`.
- Update PRD assembly and documentation to reference the config-based context.
- Remove the obsolete `openspec/project.md` file.

**Non-Goals:**
- Changing simulation, UI, or gameplay behavior.
- Altering the overall PRD content beyond updating its source references.

## Decisions

- **Use `openspec/config.yaml` as the single source of truth.** This aligns with the new OpenSpec workflow and avoids context drift.
- **Retain the existing context wording where possible.** This preserves current guidance while rehoming it.
- **Update documentation and scripts rather than adding compatibility shims.** Simpler, clearer, and avoids hidden dependencies.

## Risks / Trade-offs

- **Risk: Loss of context details during migration** → Mitigation: Move all sections verbatim where possible and review completeness.
- **Risk: Downstream scripts still reference project.md** → Mitigation: Update `make_prd.sh` and `prd.md`, then remove the file.

## Migration Plan

1. Copy the full context into `openspec/config.yaml` under `context:`.
2. Update `make_prd.sh` and `prd.md` to reference the config context.
3. Add OpenSpec quickstart info to `README.md`.
4. Delete `openspec/project.md`.

## Open Questions

- None.
