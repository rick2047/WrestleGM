# Change: Split match category from match type

## Why
Match size and match rules are separate concerns, but the current flow treats match type as both. This blocks combos like “Triple Threat Hardcore” and makes the booking flow less flexible.

## What Changes
- Introduce a match category selection step (Singles, Triple Threat, Fatal 4-Way) that defines wrestler count.
- Keep match types (Hardcore, Submission, etc.) as rule modifiers selectable via a dropdown inside match booking.
- Allow match types to restrict availability to specific categories (e.g., Ambulance is Singles-only).
- Display both category and match type in Booking Hub and Show Results.

## Impact
- Affected specs: `specs/ui/spec.md`, `specs/game-loop/spec.md`, `specs/data/spec.md`, `specs/simulation/spec.md`
- Affected code: booking flow screens, match validation, match data model, match type data, UI snapshots/flows

## UI Mockups

### Booking Hub (Slot-Level)

```text
┌──────────────────────────────────────┐
│ WrestleGM                            │
│ Show #12                             │
├──────────────────────────────────────┤
│ ▸ Match 1                            │
│   😃 Kenny Omega vs 😈 Eddie Kingston │
│   Singles · Hardcore                 │
│                                      │
│   Promo 1                            │
│   Jon Moxley                         │
│                                      │
│   Match 2                            │
│   😈 Jon Moxley vs 😃 Claudio         │
│   Triple Threat · Submission         │
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

### Match Category Selection

```text
┌──────────────────────────────────────┐
│ Select Match Category                │
├──────────────────────────────────────┤
│ ▸ Singles                             │
│                                      │
│   Triple Threat                       │
│                                      │
│   Fatal 4-Way                          │
├──────────────────────────────────────┤
│ [ Select ]   [ Cancel ]              │
└──────────────────────────────────────┘
```

### Match Booking (Filled Slot)

```text
┌──────────────────────────────────────┐
│ Book Match 3                         │
│ Triple Threat                        │
├──────────────────────────────────────┤
│ ▸ 😃 Kenny Omega                     │
│                                      │
│   😈 Eddie Kingston                  │
│                                      │
│   😃 Claudio Castagnoli              │
│                                      │
│   Match Type                          │
│   [ Submission ▾ ]                   │
│                                      │
├──────────────────────────────────────┤
│ [ Confirm ]                          │
│ [ Clear Slot ]                       │
│ [ Cancel ]                           │
└──────────────────────────────────────┘
```

### Show Results

```text
┌────────────────────────── SHOW RESULTS ──────────────────────────┐
│ WrestleGM                                                        │
│ Show #12 · RAW                                                   │
├──────────────────────────────────────────────────────────────────┤
│ Match 1                                                         │
│ Kenny Omega def. Eddie Kingston                                 │
│ Singles · Hardcore                                              │
│                                                              ★★★ │
│                                                                  │
│ Match 2                                                         │
│ Jon Moxley def. Claudio, Kenny                                  │
│ Triple Threat · Submission                                      │
│                                                              ★★★★│
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│ Show Rating: ★★★☆                                               │
│                                                                  │
│ [ Continue ]                                                    │
└──────────────────────────────────────────────────────────────────┘
```
