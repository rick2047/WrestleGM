## 1. Data and constants
- [x] 1.1 Create `data/wrestlers.json` with 12 pun-based wrestlers and baseline stats
- [x] 1.2 Create `data/match_types.json` with 3–4 match types and modifiers
- [x] 1.3 Define simulation constants and configuration defaults

## 2. Simulation engine
- [x] 2.1 Implement deterministic outcome simulation
- [x] 2.2 Implement rating simulation and star conversion
- [x] 2.3 Implement stat delta simulation and show aggregation
- [x] 2.4 Implement show-end state application and between-show recovery

## 3. Game state and rules
- [x] 3.1 Define in-memory game state models (roster, show, results, seed)
- [x] 3.2 Enforce booking rules: 3 matches, no duplicates, stamina gating

## 4. Textual UI
- [x] 4.1 Implement main menu and booking hub screens
- [x] 4.2 Implement match booking flow with wrestler and match type selection
- [x] 4.3 Implement confirmation modal, simulating screen, and results screen
- [x] 4.4 Implement roster overview screen

## 5. Tests and validation
- [x] 5.1 Add deterministic simulation tests
- [x] 5.2 Add bounds and clamp tests (ratings and stats)
- [x] 5.3 Add show rating and delta correctness tests
