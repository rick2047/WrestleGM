# Change: Add Table Formatting to CI PR Comments

## Why
The PR test comment currently lists test results in plain bullet format. Tables per class grouping will make status and reasons easier to scan while keeping the report collapsible.

## What Changes
- Render a table per class grouping in the PR test comment.
- Keep emoji status indicators and per-test reason summaries.
- Preserve collapsible group sections.
- Restrict the PR test workflow to run only when relevant files change.

## Example Comment

```markdown
<!-- pr-tests -->
## PR Test Results
Status: ✅ PASSED
Run: https://github.com/org/repo/actions/runs/123456789
Totals: ❌ 0 failed, 🛑 0 error, ⚠️ 1 skipped, ✅ 8 passed

<details>
<summary>TestMatchSimulation (tests.test_simulation_engine) (❌ 0 failed, 🛑 0 error, ⚠️ 0 skipped, ✅ 3 passed)</summary>

| Test | Status | Reason |
| --- | --- | --- |
| `test_outcome_probability_clamps` | ✅ | |
| `test_rating_bounds` | ✅ | |
| `test_alignment_modifiers` | ✅ | |

</details>

<details>
<summary>TestMutation (tests.test_simulation_engine) (❌ 0 failed, 🛑 0 error, ⚠️ 1 skipped, ✅ 1 passed)</summary>

| Test | Status | Reason |
| --- | --- | --- |
| `test_clamp_and_recovery` | ✅ | |
| `test_future_case` | ⚠️ | feature not enabled yet |

</details>
```

## Impact
- Affected specs: `specs/ci/spec.md`
- Affected code/docs: `.github/scripts/pytest_comment.py`
