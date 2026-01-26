## Context

UI tests currently load fixtures from `tests/fixtures/ui/`, which can omit wrestler images. We want image-complete fixtures, but we should not continuously mirror production data; tests must remain stable and separate.

## Goals / Non-Goals

**Goals:**
- Snapshot the current production data into test fixtures once, keeping tests deterministic.
- Ensure UI flow tests exercise wrestler images via the snapshot data.
- Keep production and test data separate going forward.

**Non-Goals:**
- Automatically syncing tests to every production data change.
- Changing production data formats or adding new runtime dependencies.

## Decisions

- **Create a one-time snapshot of current production data into UI fixtures.**
  - *Rationale:* Preserves completeness (including images) while avoiding ongoing coupling.
  - *Alternative:* Always read from `data/`; rejected to avoid drift and unexpected test changes.

- **Use a curated snapshot that already includes image-bearing wrestlers.**
  - *Rationale:* Keeps tests deterministic without adding selection logic or validations.
  - *Alternative:* Add selection/filtering logic in tests; rejected to avoid complexity.

- **Treat fixture refresh as an explicit, manual action.**
  - *Rationale:* Keeps test updates intentional and reviewable.
  - *Alternative:* Automated refresh on data changes; rejected for instability.

## Risks / Trade-offs

- **[Risk]** Snapshot can become stale relative to production data → **Mitigation:** provide a documented refresh step when needed.
- **[Risk]** Snapshot becomes stale relative to production → **Mitigation:** update the snapshot intentionally when desired.
- **[Trade-off]** Duplication of data between `data/` and `tests/fixtures/ui/` → **Mitigation:** keep scope limited to UI tests.

## Migration Plan

- Copy current production wrestler and match type data into `tests/fixtures/ui/` as the snapshot.
- Ensure the snapshot includes wrestlers with image attachments.
- Keep existing UI flow tests unchanged; rely on the snapshot to provide image-bearing wrestlers.
- Update snapshots if visual output changes.

## Open Questions

- None.
