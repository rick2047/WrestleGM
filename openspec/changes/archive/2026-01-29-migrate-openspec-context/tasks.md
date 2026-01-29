## 1. Move project context into config

- [x] 1.1 Draft a comprehensive `context:` block in `openspec/config.yaml` using existing project context and README/PRD details
- [x] 1.2 Remove `openspec/project.md` after verifying all content is migrated

## 2. Update PRD assembly inputs

- [x] 2.1 Update `make_prd.sh` to use `openspec/config.yaml` as the context source
- [x] 2.2 Update `prd.md` header/reference to point at the config-based context

## 3. Document OpenSpec usage

- [x] 3.1 Add an OpenSpec quickstart section to `README.md` with core commands and artifact locations

## 4. Verify

- [x] 4.1 Confirm no references to `openspec/project.md` remain outside change artifacts
- [x] 4.2 Run `openspec status --change "migrate-openspec-context"` to ensure tasks are ready for apply
