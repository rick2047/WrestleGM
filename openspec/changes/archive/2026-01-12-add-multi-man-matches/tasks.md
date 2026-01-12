## 1. Implementation
- [x] 1.1 Update match type data definitions with min/max wrestler counts and add Triple Threat + Fatal 4-Way entries.
- [x] 1.2 Adjust domain models (`Match`, `MatchResult`, `MatchTypeDefinition`) for wrestler lists and persisted match type IDs.
- [x] 1.3 Generalize match simulation (outcome, rating, deltas) for 2–4 wrestlers with deterministic RNG usage.
- [x] 1.4 Update validation and show booking rules to enforce match size, uniqueness, and stamina constraints.
- [x] 1.5 Update UI flow: match type selection screen, dynamic wrestler rows, booking hub/result formatting for multi-man matches.
- [x] 1.6 Add simulation tests for 2–4 wrestler outcomes, alignment modifier cases, and winner/non-winner deltas.
- [x] 1.7 Add validation tests for match size vs type, duplicates, and low-stamina booking blocks.
- [x] 1.8 Update UI tests for match type selection and multi-man booking flows (row counts, selection, type changes).
- [x] 1.9 Validate with `pytest` and any existing UI snapshot tests.
