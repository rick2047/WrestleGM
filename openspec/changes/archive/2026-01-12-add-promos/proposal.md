# Change: Add promo slots, booking, and simulation

## Why
The current MVP only supports three matches per show. Promos are required to match the PRD for show cards and to add non-match booking choices that still affect ratings and progression.

## What Changes
- Add two promo slots to the show card (Match 1, Promo 1, Match 2, Promo 2, Match 3).
- Add promo booking UI flow (single wrestler) and reuse the existing wrestler selection screen.
- Extend roster data with a `mic_skill` attribute used in promo quality.
- Simulate promo quality, stars, popularity deltas, and stamina recovery.
- Compute show rating as the average of all slot ratings (matches + promos).
- Update booking validation to allow low-stamina wrestlers in promo slots while still blocking duplicates.

## Impact
- Affected specs: `specs/ui/spec.md`, `specs/simulation/spec.md`, `specs/game-loop/spec.md`, `specs/data/spec.md`
- Affected code: UI booking hub, booking screens, simulation engine, show applier, data loaders

## UI Mockups

### Show Screen (Slot-Level)
```text
┌──────────────────────────────────────┐
│ WrestleGM                            │
│ Show #12                             │
├──────────────────────────────────────┤
│ ▸ Match 1                            │
│   Kenny Omega vs Eddie Kingston      │
│   Type: Singles                      │
│                                      │
│   Promo 1                            │
│   Jon Moxley                         │
│                                      │
│   Match 2                            │
│   Jon Moxley vs Claudio Castagnoli   │
│   Type: Hardcore                     │
│                                      │
│   Promo 2                            │
│   [ Empty ]                          │
│                                      │
│   Match 3                            │
│   [ Empty ]                          │
│                                      │
├──────────────────────────────────────┤
│ [ Run Show ] (disabled)              │
│ [ Back ]                             │
└──────────────────────────────────────┘
```

### Promo Booking (Empty Slot)
```text
┌──────────────────────────────────────┐
│ Book Promo 1                         │
├──────────────────────────────────────┤
│ ▸ Wrestler                           │
│   [ Empty ]                          │
│                                      │
├──────────────────────────────────────┤
│ [ Confirm ] (disabled)               │
│ [ Clear Slot ] (disabled)            │
│ [ Cancel ]                           │
└──────────────────────────────────────┘
```

### Promo Booking (Filled Slot)
```text
┌──────────────────────────────────────┐
│ Book Promo 1                         │
│ Jon Moxley                           │
├──────────────────────────────────────┤
│ ▸ Wrestler                           │
│   Jon Moxley                         │
│                                      │
├──────────────────────────────────────┤
│ [ Confirm ]                          │
│ [ Clear Slot ]                       │
│ [ Cancel ]                           │
└──────────────────────────────────────┘
```

### Wrestler Selection (Shared)
```text
Select Wrestler (Promo 1)

| Name                 | Sta | Pop     |
| -------------------- | --- | ------- |
| 😃 Kenny Omega       |  28 |  92 🥱 📅 |
| 😈 Jon Moxley        |  12 |  88 🥱   |
| 😃 Eddie Kingston    |  64 |  74     |

⛔ Already booked in another slot

[ Select ]   [ Cancel ]
```

### Confirmation Modal (Shared)
```text
┌──────────────────── CONFIRM BOOKING ────────────────────────┐
│ Book Promo 1 with Jon Moxley?                                │
│                                                              │
│ > Confirm                                                    │
│   Cancel                                                     │
└──────────────────────────────────────────────────────────────┘
```

### Show Results
```text
┌────────────────────────── SHOW RESULTS ──────────────────────────┐
│ WrestleGM                                                        │
│ Show #12 · RAW                                                   │
├──────────────────────────────────────────────────────────────────┤
│ Match 1                                                         │
│ Kenny Omega def. Eddie Kingston                                 │
│ Type: Singles                                                   │
│                                                              ★★★ │
│                                                                  │
│ Promo 1                                                         │
│ Jon Moxley                                                      │
│                                                              ★★  │
│                                                                  │
│ Match 2                                                         │
│ Jon Moxley def. Claudio Castagnoli                               │
│ Type: Hardcore                                                  │
│                                                              ★★★★│
│                                                                  │
│ Promo 2                                                         │
│ Maria Blaze                                                     │
│                                                              ★★  │
│                                                                  │
│ Match 3                                                         │
│ Alpha def. Beta                                                 │
│ Type: Tag                                                       │
│                                                              ★★★ │
├──────────────────────────────────────────────────────────────────┤
│ Show Rating: ★★★☆                                               │
│                                                                  │
│ [ Continue ]                                                    │
└──────────────────────────────────────────────────────────────────┘
```
