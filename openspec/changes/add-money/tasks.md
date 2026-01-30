## 1. Data and model updates

- [ ] 1.1 Add `base_cost` to `data/match_types.json` and update match type loader to default missing `base_cost` to 0
- [ ] 1.2 Add `money` to `GameState` with a starting value for new sessions

## 2. Economy calculations

- [ ] 2.1 Implement wrestler booking price calculation (`BASE + A * (pop ** 1.2)`) and unique-wrestler aggregation per show
- [ ] 2.2 Compute `show_cost` from unique wrestler prices plus match type `base_cost`
- [ ] 2.3 Compute audience inputs (`pop_sum`, `align_score`, `rivalry_count`, `cooldown_count`) for a booked card
- [ ] 2.4 Implement audience curve with `base_from_pop(pop_sum) = pop_sum * 20`, rivalry/alignment bonuses, cooldown penalties, clamp to >= 0
- [ ] 2.5 Implement deterministic RNG swing multipliers (0.8..1.2) with independent draws for audience and merch
- [ ] 2.6 Compute `gate_income = audience * GATE_RATE` with default `GATE_RATE = 1`
- [ ] 2.7 Compute `merch_rate` curve and `merch_income = audience * merch_rate(show_rating)` with clamp to 0.50
- [ ] 2.8 Update money after results: `money = money - show_cost + gate_income + merch_income`

## 3. Simulation pipeline integration

- [ ] 3.1 Insert economy computation stage after ratings and before show application, preserving RNG order
- [ ] 3.2 Ensure economy RNG uses the session-seeded RNG and does not affect match/promo RNG draws

## 4. Bankruptcy gating

- [ ] 4.1 Implement `min_valid_show_cost` calculation for any valid 3-match, 2-promo card
- [ ] 4.2 Check bankruptcy when attempting to book the next show and route to Game Over: Bankruptcy when `current_money < min_valid_show_cost`

## 5. UI updates

- [ ] 5.1 Booking Hub: show current money (red if negative), total show cost, rivalry/cooldown counts, and per-match cost label
- [ ] 5.2 Run Show confirmation modal: add debt warning when cost exceeds money and keep After Show as `$—`
- [ ] 5.3 Results screen: display audience, gate income, merch income, total earned, and current money
- [ ] 5.4 Game Over: Bankruptcy screen with final money and Main Menu action

## 6. Tests

- [ ] 6.1 Add deterministic tests for audience and merch RNG swings (0.8..1.2)
- [ ] 6.2 Add tests for show cost computation and unique wrestler billing
- [ ] 6.3 Add tests for bankruptcy gating with `min_valid_show_cost`
