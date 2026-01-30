## Why

The game currently has no economic stakes, so booking decisions are always optimal and risk-free. Adding money, audience, and bankruptcy creates scarcity and tradeoffs that make show-to-show management meaningful now.

## What Changes

- Track promotion-level money and allow it to go negative after a show.
- Compute wrestler booking price from popularity and charge once per show (unique wrestlers only).
- Add match type base costs to total show cost.
- Generate audience from card popularity, alignment, rivalries, and cooldowns with deterministic RNG.
- Compute gate and merch income from audience and show quality; apply after show completion.
- Allow running a show even if it creates debt; trigger bankruptcy if the next valid show cannot be afforded.
- Update booking hub, confirm-run modal, show results, and game over UI to surface money/audience and debt warnings.

## Capabilities

### New Capabilities
- `economy`: Money, audience, costs, income, debt, and bankruptcy rules for the show loop.

### Modified Capabilities
- `data`: Match type definitions include base cost.
- `game-loop`: Show flow updates money and enforces bankruptcy at show boundaries.
- `simulation`: Audience and income calculations added to deterministic simulation.
- `rivalry`: Rivalry/cooldown data contributes to audience demand.
- `ui`: Booking hub, confirm modal, results, and bankruptcy screens display money/audience.

## Impact

- Data files: add `base_cost` to `data/match_types.json` and ensure loaders support it.
- Simulation pipeline: new audience/gate/merch calculations and cost aggregation.
- Game state: money field and bankruptcy checks at show boundaries.
- UI screens: booking hub cost rollups, debt warnings, results breakdown, and bankruptcy screen.
