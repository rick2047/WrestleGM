## 1. Implementation
- [ ] 1.1 Add a match type bonus modifier (e.g., `MatchTypeBonusModifier`) that returns the rating bonus in 0–100 space.
- [ ] 1.2 Refactor `SimulationEngine.simulate_rating` to remove the separate rating bonus addition and rely on the modifier list instead.
- [ ] 1.3 Update tests to cover the unified modifier flow and ensure ratings remain unchanged.
- [ ] 1.4 Update PRD/spec docs if needed to reflect the unified modifier flow.
- [ ] 1.5 Run all tests and ensure they pass.
