# Change: Add Wrestler View UI and booking card layout

## Why
The current booking UI is list-heavy and low on wrestler identity. This change makes booking feel like assembling a card while keeping the interface readable in narrow terminals.

## What Changes
- Add a reusable Wrestler View component with avatar rendering, stats, and optional rivalry/description blocks.
- Redesign Match Booking into a single narrow card with inline wrestler-count selection and a rivalry summary header.
- Update Promo Booking to use a single Wrestler View without rivalry data.
- Extend wrestler data with description and avatar_path, mapped to local assets in `data/images/`.
- Add a Wrestler Selection inspect modal (table-first selection remains; `i` inspects).
- Update UI snapshots and flows for the new layouts.

## Impact
- Affected specs: `specs/ui/spec.md`, `specs/data/spec.md`, `specs/ui-testing/spec.md`
- Affected code: UI widgets/screens, wrestler data model, data loading, image rendering

## UI Mockups

### Wrestler View (Inspection Context, filled)
```text
┌──────────────────────────────────────────────┐
│ ┌───────────────┐ 😃 Kazuchika Okada         │
│ │  avatar.png   │ ⭐92  🔋28  🎤88            │
│ │ (half render) │ "Ace of the Rainmaker era, │
│ └───────────────┘  calm, precise, relentless."
│                                              │
│ Rivalries                                     │
│  💥 Kenny Omega                               │
│  ⚔️ Tetsuya Naito                             │
│  🔥 Jay White                                 │
└──────────────────────────────────────────────┘
```

### Wrestler View (Empty)
```text
┌──────────────────────────────────────────────┐
│ ┌───────────────┐ Select Wrestler            │
│ │ placeholder   │                            │
│ │ (half render) │                            │
│ └───────────────┘                            │
└──────────────────────────────────────────────┘
```

### Match Booking
```text
┌──────────────────────────────────────────────┐
│ Match #1        💥 x3  ⚔️ x1                  │
├──────────────────────────────────────────────┤
│ Wrestlers: [ 3 ▾ ]    Type: [ ▾ ]             │
│                                              │
│ Wrestlers (VerticalScroll)                    │
│  ▶ ┌───────────────┐ 😃 Kazuchika Okada       │
│    │ avatar.png    │ ⭐92  🔋28  🎤88          │
│    │ (half render) │ 💥 ⚔️ 🔥                 │
│    └───────────────┘                          │
│                                              │
│    ┌───────────────┐ 😈 Jay White             │
│    │ avatar.png    │ ⭐85  🔋40  🎤70          │
│    │ (half render) │ 💥 🔥                    │
│    └───────────────┘                          │
│                                              │
│    ┌───────────────┐ Select Wrestler          │
│    │ placeholder   │                          │
│    │ (half render) │                          │
│    └───────────────┘                          │
│                                              │
│ [ Clear Slot ]   [ Confirm ]   [ Back ]       │
└──────────────────────────────────────────────┘
```

### Promo Booking (Empty)
```text
┌──────────────────────────────────────────────┐
│ Promo Slot #2                                 │
├──────────────────────────────────────────────┤
│ Type: [ Promo ▾ ]                             │
│                                              │
│ Performer                                     │
│  ▶ ┌───────────────┐ Select Wrestler          │
│    │ placeholder   │                          │
│    │ (half render) │                          │
│    └───────────────┘                          │
│                                              │
│ [ Clear Slot ]   [ Confirm ]   [ Back ]       │
└──────────────────────────────────────────────┘
```

### Wrestler Selection (Inspect Modal Open)
```text
┌──────────────────────────────────────────────┐
│ Select Wrestler                               │
├──────────────────────────────────────────────┤
│ Name            ⭐   🔋   🎤   Align            │
│ ▶ Okada           92   28   88   😃            │
│   Jay White       85   40   70   😈            │
│   Naito           88   35   82   😃            │
│   Omega           90   30   85   😃            │
│                                              │
│ ┌──────────────────────────────────────────┐ │
│ │ Wrestler Details                          │ │
│ │ ┌───────────────┐ 😃 Kazuchika Okada     │ │
│ │ │ avatar.png    │ ⭐92  🔋28  🎤88        │ │
│ │ │ (half render) │ "Ace of the Rainmaker…"│ │
│ │ └───────────────┘                          │ │
│ │                                            │ │
│ │ Rivalries                                   │ │
│ │  💥 Kenny Omega                             │ │
│ │  ⚔️ Tetsuya Naito                           │ │
│ │  🔥 Jay White                               │ │
│ │                                            │ │
│ │              [ Esc to close ]               │ │
│ └──────────────────────────────────────────┘ │
└──────────────────────────────────────────────┘
```
