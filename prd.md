# WrestleGM – Textual MVP Product Requirements Document

> **Living document**: This PRD defines the full MVP for WrestleGM as a **Textual-based wrestling management game**. It is intended to be iteratively expanded and refined together. This document establishes the foundation for a complete MVP focused on *show-by-show progression*.

---

## 1. Vision & Goals

### 1.1 Product Vision

WrestleGM is a **terminal-first wrestling management game** where the player runs a wrestling promotion **one show at a time**. Each show consists of a booked card of matches, and the core pleasure of the game comes from watching how wrestler stats evolve **across shows**, not from winning a single match.

The experience should feel:

- Systemic, not scripted
- Deterministic but expressive
- Focused on *long-term progression*
- Playable entirely via keyboard
- Comfortable on narrow terminals

---

### 1.2 MVP Goals (Show-Centric)

The MVP must allow a player to:

- Run an **ongoing series of shows** (weekly, episodic, or abstract)
- Book matches and promos for each show
- Select match types that meaningfully affect match outcomes
- Simulate matches and promos to complete an entire show
- Receive an **overall show rating** derived from slot quality
- Advance from show to show and **observe stat evolution over time**
- Make booking decisions based on fatigue, popularity, and long-term impact

The primary success criterion of the MVP is:

> *After multiple shows, the roster and show quality clearly change based on player booking decisions.*

Outcomes:

- A repeatable **show → results → progression** loop
- Clear cause-and-effect between booking, match quality, and long-term stats
- Extensible systems with no hardcoded content

---

## 2. Design Principles

- **Show-first design**: All progression is evaluated at show boundaries
- **Textual-first UI**: Widgets and CSS are the source of consistency
- **Data-driven domain**: Wrestlers, match types, and rules come from data files
- **Deterministic simulation**: Same inputs + seed = same results
- **Keyboard-only navigation**: No mouse assumptions
- **Explicit systems**: Outcomes are explainable via numbers, not hidden scripts

---

## 2.1 CI & Automation (PR Validation)

These rules define how pull requests are validated in CI.

- Pull requests run automated tests via `uv run pytest`.
- PR test results are posted as a single sticky comment that updates on each run.
- The comment lists test cases grouped by class in collapsible sections with per-test emoji statuses:
  - ✅ passed
  - ❌ failed
  - 🛑 error
  - ⚠️ skipped
- Workflow permissions are minimal: read repository contents, write PR comments.
- PR test workflow runs only when changes touch:
  - `tests/**`
  - `wrestlegm/**`
  - `data/**`
  - `main.py`
  - `pyproject.toml`
  - `uv.lock`
  - `.github/workflows/pr-tests.yml`

---

## 3. Core Game Loop (MVP)

1. Start from Main Menu and select New Game
2. Land on the Game Hub (session home)
3. Open the current show overview / booking hub
4. Build or review the show card
5. Book matches and promos (wrestlers + match types for matches)
6. Run the show (simulate slots sequentially)
7. Review results and **overall show rating**
8. Return to the Game Hub and advance to the next show

The game loop is **show-driven**, not match-driven.

---

## 4. Domain Model (Data-Driven)

### 4.1 WrestlerDefinition

Loaded from `data/wrestlers.json`.

Fields:

- `id: string` (stable, unique)
- `name: string`
- `alignment: Face | Heel`
- `popularity: int (0–100)`
- `stamina: int (0–100)`
- `mic_skill: int (0–100)`

Future-safe (not required for MVP):

- style
- tags
- injury\_status

---

### 4.2 MatchTypeDefinition

Loaded from `data/match_types.json`.

Fields:

- `id: string`
- `name: string`
- `description: string`
- `modifiers`:
  - `outcome_chaos`
  - `rating_bonus`
  - `rating_variance`
  - `stamina_cost_winner`
  - `stamina_cost_loser`
  - `popularity_delta_winner`
  - `popularity_delta_loser`

Match types **must affect simulation**.

---

### 4.3 Match

Represents a booked match within a show.

Fields:

- `wrestler_a_id`
- `wrestler_b_id`
- `match_type_id`

---

### 4.4 Promo

Represents a booked promo within a show.

Fields:

- `wrestler_id`

---

### 4.5 Show

Represents a single event in the game timeline.

Fields:

- `show_index`
- `scheduled_slots: [Match | Promo]`
- `results: [MatchResult | PromoResult]`
- `show_rating`

A show is the **atomic unit of progression**.

---

### 4.6 MatchResult

Immutable result of simulation.

Fields:

- `winner_id`
- `loser_id`
- `rating`
- `match_type_id`
- `applied_modifiers`
- `stat_deltas`

---

### 4.7 PromoResult

Immutable result of promo simulation.

Fields:

- `wrestler_id`
- `rating`
- `stat_deltas`

---

## 5. Simulation System

The simulation layer is deterministic, side-effect free, and composed of match and promo simulations plus one aggregation step. The following rules apply to *every slot* in a show.

---

### 5.1 Simulation Pipeline (Authoritative)

For each slot, the engine executes the following pipeline:

1. **Match Outcome Simulation** → determines winner / loser (matches only)
2. **Rating Simulation** → determines slot quality (stars)
3. **Stat Delta Simulation** → determines progression deltas (no mutation)

After *all* slots in a show complete:

4. **Show Rating Aggregation** → derives overall show rating
5. **State Application** → applies all stat deltas at show end

No other simulation steps exist in the MVP.

Implementation ownership:

- `SimulationEngine` owns RNG and match simulation steps.
- `ShowApplier` applies deltas and recovery at show end.

---

### 5.2 Determinism & RNG Governance

**Single RNG rule**

- All randomness must flow through a single RNG instance seeded from game state.
- The seed is stored in global state and must be persisted.

**Reproducibility rule**

- Given identical inputs (roster stats, match type config, show card, and seed), the simulation must always return identical outputs (winners, match ratings, deltas, show rating).

**No hidden inputs**

- Simulation must not depend on wall-clock time, UI focus, ordering artifacts, or any non-explicit state.

**RNG usage discipline**

- Outcome simulation uses exactly one RNG draw per match (the final probability sample).
- Rating simulation uses one RNG draw per match (variance swing).
- Show rating uses no RNG.

---

### 5.3 Outcome Simulation (Who Wins)

**Purpose** Determine the winner and loser for a match based on deterministic “power” and match-type “chaos”.

**Inputs**

- Wrestler A: `popularity`, `stamina`
- Wrestler B: `popularity`, `stamina`
- Match type: `outcome_chaos` (float 0.0–1.0)
- Tunable constants: `P_WEIGHT`, `S_WEIGHT`, `D_SCALE`, `P_MIN`, `P_MAX`
- Seeded RNG

**Step A — Deterministic power** Power is calculated without randomness:

- `power = popularity * P_WEIGHT + stamina * S_WEIGHT`

Constraints:

- Popularity and stamina are expected to be in `0–100`.
- `P_WEIGHT + S_WEIGHT = 1.0` is recommended.

**Step B — Power difference to base win probability**

- `diff = power_A - power_B`
- `p_base = 0.5 + (diff / D_SCALE)`
- `p_base = clamp(p_base, P_MIN, P_MAX)`

Interpretation:

- `D_SCALE` controls how quickly power advantage becomes a strong favorite.
- `P_MIN/P_MAX` prevent absolute certainty.

**Step C — Apply match-type chaos (variance-only design)** Match types affect outcome only by pulling probability toward 50/50:

- `p_final = lerp(p_base, 0.5, outcome_chaos)`

Where:

- `outcome_chaos = 0.0` → purely power-based
- `outcome_chaos = 1.0` → always 50/50

**Step D — Sample winner**

- draw `r = rng.random()` in `[0,1)`
- if `r < p_final` → A wins else B wins

**Outputs**

- `winner_id`, `loser_id`

**Recommended debug payload (for testing & balancing)**

- `power_A`, `power_B`, `diff`
- `p_base`, `outcome_chaos`, `p_final`
- `r` (sample)

---

### 5.4 Rating Simulation (How Good It Was)

**Purpose** Assign a match quality rating in **0.0–5.0 stars**, independent of who won.

**Inputs**

- Wrestler A & B: `popularity`, `stamina`, `alignment`
- Match type: `rating_bonus`, `rating_variance`
- Tunable constants: `POP_W`, `STA_W`, `ALIGN_BONUS`
- Seeded RNG

**Internal representation** Rating is first computed in `0–100` space for ease of tuning, then converted to stars.

**Step A — Compute deterministic base in 0–100**

- `pop_avg = (popA + popB) / 2`
- `sta_avg = (staA + staB) / 2`
- `base_100 = pop_avg * POP_W + sta_avg * STA_W`

Priority guarantee:

- Popularity is priority 1 (so `POP_W > STA_W`).
- Stamina is priority 2.

**Step B — Alignment modifier (wrestling psychology)** Alignment affects rating only:

- Face vs Heel → `alignment_mod = +ALIGN_BONUS`
- Heel vs Heel → `alignment_mod = -2 * ALIGN_BONUS`
- Face vs Face → `alignment_mod = 0`

Then:

- `base_100 += alignment_mod`

**Step C — Match type rating bonus**

- `base_100 += rating_bonus`

**Step D — Apply rating variance (after deterministic logic)**

- `swing = rng.randint(-rating_variance, +rating_variance)`
- `rating_100 = base_100 + swing`

**Step E — Clamp 0–100**

- `rating_100 = clamp(rating_100, 0, 100)`

**Step F — Convert to 0–5 stars**

- `rating_stars = round((rating_100 / 100) * 5, 1)`

**Outputs**

- `match_rating_stars` (0.0–5.0)

**Recommended debug payload**

- `pop_avg`, `sta_avg`
- `base_100`, `alignment_mod`
- `rating_bonus`, `rating_variance`, `swing`
- `rating_100`, `rating_stars`

---

### 5.5 Promo Rating Simulation (How Good It Was)

**Purpose** Assign a promo quality rating in **0.0–5.0 stars** based on mic skill and popularity.

**Inputs**

- Wrestler: `mic_skill`, `popularity`
- Tunable constants: `PROMO_VARIANCE`
- Seeded RNG

**Step A — Compute deterministic base in 0–100**

- `base_100 = mic_skill * 0.7 + popularity * 0.3`

**Step B — Apply rating variance**

- `swing = rng.randint(-PROMO_VARIANCE, +PROMO_VARIANCE)`
- `rating_100 = base_100 + swing`

**Step C — Clamp 0–100**

- `rating_100 = clamp(rating_100, 0, 100)`

**Step D — Convert to 0–5 stars**

- `rating_stars = round((rating_100 / 100) * 5, 1)`

---

### 5.6 Promo Stat Delta Simulation (Progression Impact)

**Purpose** Produce progression deltas for promo performers.

**Popularity deltas**

- If `rating_100 < 50` → `Δpop = -5`
- If `rating_100 ≥ 50` → `Δpop = +5`

**Stamina deltas**

- `Δsta = floor(STAMINA_RECOVERY_PER_SHOW / 2)`

---

### 5.7 Match Stat Delta Simulation (Progression Impact)

**Purpose** Produce progression deltas for winner and loser. This system produces deltas only and never mutates roster state.

**Inputs**

- Match outcome: `winner_id`, `loser_id`
- Match type modifiers:
  - `popularity_delta_winner`
  - `popularity_delta_loser`
  - `stamina_cost_winner`
  - `stamina_cost_loser`

**Popularity deltas (data-driven)**

- `Δpop_winner = popularity_delta_winner`
- `Δpop_loser = popularity_delta_loser`

Notes:

- Loser popularity delta may be **positive, zero, or negative**.
- Match rating does **not** affect popularity in MVP.

**Stamina deltas (fixed for MVP)**

- `Δsta_winner = -stamina_cost_winner`
- `Δsta_loser = -stamina_cost_loser`

Notes:

- Stamina cost is fixed per match type.
- Match rating does **not** scale stamina costs in MVP.

**Outputs**

- `stat_deltas[winner_id] = {popularity: Δpop_winner, stamina: Δsta_winner}`
- `stat_deltas[loser_id]  = {popularity: Δpop_loser,  stamina: Δsta_loser}`

---

### 5.8 Show Rating Aggregation

**Purpose** Compute an overall show quality rating derived from slot ratings.

**Rules (MVP)**

- Each slot produces a star rating.
- Show rating is the arithmetic mean of all slot ratings:
  - `show_rating = average(slot_ratings[])`

Constraints:

- Must be computed after all matches are simulated.
- Deterministic aggregation (no RNG).
- If there are no match ratings, the show rating is `0.0`.

---

### 5.9 State Application at Show End

**Purpose** Apply all deltas once a show completes. This is the only moment the roster changes.

Rules:

- Apply deltas for each wrestler exactly once.
- Clamp after application:
  - Popularity is clamped to `0–100`.
  - Stamina is clamped to `0–100`.
- State mutation is owned by a dedicated `ShowApplier` and triggered via `GameState.run_show()`.

Ordering:

- The order of applying deltas must not change results.
- Recommended approach: compute all new values first, then commit.

---

### 5.10 Required Tests for Simulation

Minimum required tests:

- Determinism: same inputs + seed → identical outputs
- Outcome sanity: probabilities clamp to bounds
- Rating bounds: always 0.0–5.0 stars
- Promo determinism: same inputs + seed → identical promo ratings and deltas
- Promo deltas: threshold produces -5/+5 and stamina recovery
- Delta correctness: winner/loser deltas match match-type config
- Show rating: equals mean of slot ratings
- Clamp tests: stats never exceed 0–100 after application

---

## 6. Show Structure Rules

This section defines how a **show** is structured, what constraints apply when booking it, and how it interacts with the simulation system. These rules are part of the MVP and intentionally simple but explicit.

---

### 6.1 What a Show Is

A **Show** is the atomic unit of progression in WrestleGM.

A show:

- Consists of a finite list of match and promo slots (the card)
- Is fully booked before simulation starts
- Is simulated slot-by-slot in a fixed order
- Produces:
  - Match and promo results
  - Match and promo ratings
  - A single overall show rating
- Applies all stat changes only at show end

Once a show begins simulation, its card is **locked**.

---

### 6.2 Card Size (MVP)

For MVP, show size is intentionally fixed.

**Rules**

- Each show consists of **exactly 3 matches and 2 promos**
- The order of slots matters only for presentation, not simulation
- No weighting (e.g. main event bonus) is applied in MVP

Rationale:

- Forces meaningful booking decisions
- Keeps pacing tight
- Simplifies UI and testing

---

### 6.3 Match Slots & Booking Flow

A show card contains ordered slots:

- Slot 1: Match
- Slot 2: Promo
- Slot 3: Match
- Slot 4: Promo
- Slot 5: Match

Each slot must be fully specified before the show can run:

- Wrestler A
- Wrestler B
- Match Type
- Promo Wrestler (for promo slots)

A show cannot be simulated unless **all slots are valid**.

---

### 6.4 Wrestler Usage Constraints (MVP)

**Per-show constraints**

- A wrestler may appear in **only one slot per show** (match or promo)

**Validation rules**

- Once a wrestler is selected in any slot, they are unavailable for other slots
- Attempting to select an unavailable wrestler must be blocked in UI

Rationale:

- Prevents overbooking exploits
- Keeps stamina meaningful

---

### 6.5 Availability & Fatigue (MVP)

For MVP, availability is binary and derived directly from stamina.

**Rules**

- Wrestlers with stamina ≤ `STAMINA_MIN_BOOKABLE` cannot be booked in matches
- Low-stamina wrestlers are allowed in promo slots
- Default recommendation: `STAMINA_MIN_BOOKABLE = 10`

Notes:

- No injuries in MVP
- No partial availability
- Recovery is handled between shows (future section)

---

### 6.6 Show Lifecycle

A show progresses through the following states:

1. **Planning**

   - Player books the card
   - Slots can be edited

2. **Locked**

   - Card is complete
   - No edits allowed

3. **Simulating**

   - Matches are simulated sequentially
   - UI shows progress

4. **Completed**

   - Results available
   - Show rating visible
   - Stat deltas ready to apply

5. **Applied**

   - Stat deltas applied
   - Game advances to next show

These states must be explicit in code.

---

### 6.7 Ordering Guarantees

- Slots are simulated in card order
- Simulation order does **not** affect outcomes or ratings in MVP
- All stat deltas are applied together at show end

---

### 6.8 Required Validation Checks

Before a show can be run:

- Card has exactly 3 matches and 2 promos
- Each promo has a wrestler assigned
- No duplicate wrestlers across slots
- All match-booked wrestlers meet stamina requirements
- All match slots have a valid match type

The UI must prevent invalid shows from being run.

---

## 7. Between-Show Recovery Rules

This section defines how wrestlers recover between shows. Recovery is applied **once per show transition** and depends on whether a wrestler worked on the previous show.

---

### 7.1 Recovery Timing

Recovery occurs:

- After a show is completed
- After all stat deltas from the show are applied
- Before the next show enters the Planning state

Recovery is never applied mid-show.

---

### 7.2 Recovery Eligibility (MVP)

Recovery is **participation-based**.

**Rules**

- Wrestlers who **appeared in any match or promo on the previous show recover no stamina**
- Wrestlers who **did not appear on the show recover stamina**

This makes rest a meaningful booking decision.

---

### 7.3 Stamina Recovery Amount (MVP)

**Rule**

- Eligible (resting) wrestlers recover a fixed amount of stamina.

**Default value**

- `STAMINA_RECOVERY_PER_SHOW = +15`

**Application**

- Recovery applies only to wrestlers who did not appear in any match or promo on the show
- Stamina is clamped to `0–100` after recovery

---

### 7.4 Rationale

- Creates a clear trade-off between using top stars and letting them rest
- Prevents infinite stamina loops
- Encourages roster rotation
- Keeps the system simple but strategically meaningful

---

### 7.5 Explicit Non-Rules (MVP)

The following do **not** exist in MVP:

- Partial recovery for working wrestlers
- Variable recovery based on match rating
- Bonus recovery for main events
- Injuries or lingering fatigue states
- Time-based simulation between shows

These are intentionally deferred.

---

### 7.6 Determinism Guarantee

- Recovery uses no RNG
- Given identical state, recovery always produces identical results

---

## 8. User Experience & Interaction Model

This section defines the **full MVP UX** for WrestleGM, including screens, navigation, validation philosophy, visual indicators, and widget mapping. The UX is designed to be **terminal-first**, keyboard-only, and intentionally opaque where appropriate.

---

### 8.1 UX Design Principles

- Keyboard-only interaction
- Narrow-terminal friendly (≤40 columns)
- No projections, odds, or system hints
- The UI blocks only **logical contradictions**, never **strategic mistakes**
- The player learns systems through repetition and consequence
- **A global footer is always present to show key bindings only**

---

### 8.2 Global Navigation Rules

**Universal keys**

- `↑ / ↓` – move within vertical lists
- `← / →` – move between horizontal fields or buttons (where applicable)
- `Enter` – activate focused element
- `Esc` – back / cancel (context-dependent; no effect on Game Hub)
- `Q` – quit (Main Menu, Game Hub)
- Arrow-key focus loops between lists and action buttons; disabled actions are skipped
- Focus wraps from last to first and first to last within a screen’s focusable controls

**Navigation stack**

- Screens are pushed and popped on a stack
- Selecting an item pops automatically
- Esc pops the current context unless focus is trapped (e.g. modal); Game Hub ignores Esc

**Session persistence rule**

- Temporary state inside a screen (e.g. Match Booking) **persists across subscreens**
- Entering Wrestler Selection or Match Type Selection does not reset in-progress selections
- Temporary state is discarded only when the user explicitly cancels the parent screen

---

### 8.3 Visual Indicator Language

The game uses a **minimal, consistent emoji language**:

| Indicator | Meaning                                         | Blocks Action |
| --------- | ----------------------------------------------- | ------------- |
| ⚠️        | Empty / incomplete field                        | Yes           |
| ⛔         | Logical impossibility (e.g. duplicate wrestler) | Yes           |
| 🥱        | Low stamina / fatigued                          | Yes           |
| 📅        | Already booked in another slot                  | Yes           |

Indicators rely on iconography first; color is supplemental.

Alignment is shown by prefixing the wrestler name with an emoji (Face 😃, Heel 😈).

---

### 8.4 Validation Philosophy

- Validation is **binary** at the moment of committing an action
- The system blocks only impossible states
- Low stamina is treated as **unbookable for matches** and is blocked
- Low stamina is allowed for promo booking
- No warnings or advice are shown beyond visual indicators and short inline errors
- Temporary booking state persists until explicitly cancelled

---

### 8.5 Screen List (MVP)

### 8.5.1 Global Footer & Keybinding Display

All screens in WrestleGM include Textual’s built-in **Footer** widget.

**Rules**

- The footer is always visible
- It displays **key bindings only**
- No game state, stats, or hints are shown in the footer
- The footer is the authoritative source for "what actions are available right now"

**Behavior**

- Footer content updates automatically based on focus
- When a modal is open, only modal bindings are shown
- Hidden or internal bindings must not appear in the footer

This ensures discoverability without clutter and keeps the UI self-teaching.

---



The MVP consists of the following screens:

1. Main Menu
2. Game Hub
3. Show Overview / Booking Hub
4. Match Booking (single-slot editor)
5. Promo Booking (single-slot editor)
6. Wrestler Selection
7. Match Type Selection
8. Match Confirmation
9. Simulating Show
10. Show Results
11. Roster Overview

---

### 8.6 Main Menu

**Purpose**

- Entry point and global navigation
- Meta-only screen; gameplay is reachable only via New Game

**Components**

- Vertical menu list:
  - New Game
  - Quit
- Static footer metadata (non-persistent context only)

**Focus**

- Menu list only

**Behavior**

- Enter selects
- Esc has no effect
- Q quits

---

### 8.7 Game Hub

The Game Hub is the **session-level home screen** and the only gateway into gameplay.

**Purpose**

- Provide a safe, non-simulating state between shows
- Route to booking and roster views
- Allow explicit exit to the Main Menu

**Components**

- Current show action: Book Current Show
- Descriptive subtitle line showing the current show number
- Roster Overview
- Exit to Main Menu

**Behavior**

- Enter selects the focused option
- Esc has no effect
- Q quits the application
- Exiting to Main Menu ends the current session

---

### 8.8 Show Overview / Booking Hub

The Booking Hub is a **slot-level overview screen**. It shows the current show card and allows the player to choose *which match* to edit.

**Purpose**

- View the full show card at a glance
- Select a match slot to edit
- Run the show once all slots are booked

**Components**

- Show header (show number)
- List of 5 slots in fixed order (Match 1, Promo 1, Match 2, Promo 2, Match 3)
- Footer actions:
  - Run Show
  - Back (return to Game Hub)

**Slot states**

- Empty: slot has no assignment
- Booked: slot contains a fully valid match (A, B, Type) or promo (Wrestler)

Slots are binary; partial matches do not exist on the show.

**Focus model**

- `↑ / ↓` moves between slots
- `Enter` opens the booking screen for the focused slot

**Validation rules**

- Run Show is enabled only when the show card has no validation errors
- Booking Hub never accepts invalid or partial slots

---

### 8.9 Match Booking Screen

This screen is the **only place where a match can be edited or created**. It owns all booking validation.

**Purpose**

- Define a complete match for a single slot

**Editable fields**

- Wrestler A
- Wrestler B
- Match Type

**Behavior**

- Fields open their respective selection screens on Enter
- Confirm is enabled only when all three fields are valid
- Esc or Cancel discards all changes and returns to Booking Hub
- Clear Slot removes the match and returns to Booking Hub
- Clear Slot is disabled if the slot is empty
- If the slot is empty, the match type defaults to the first available match type

**Validation rules (authoritative)**

- Wrestler A and Wrestler B must both be set
- Wrestler A ≠ Wrestler B
- Wrestlers already booked in other slots cannot be selected
- Match Type must be set
- Wrestlers below `STAMINA_MIN_BOOKABLE` cannot be selected
- Low stamina is indicated with 🥱 where displayed

No invalid match can ever be written to the show.

---

### 8.10 Promo Booking Screen

This screen edits a single promo slot and uses the shared wrestler selection screen.

**Purpose**

- Define a complete promo for a single slot

**Editable fields**

- Wrestler

**Behavior**

- Wrestler field opens the wrestler selection screen on Enter
- Confirm is enabled only when the wrestler is set
- Esc or Cancel discards all changes and returns to Booking Hub
- Clear Slot removes the promo and returns to Booking Hub
- Clear Slot is disabled if the slot is empty
- Low-stamina wrestlers are selectable for promos

---

### 8.11 Wrestler Selection Screen

**Components**

- Wrestler table with Name/Sta/Mic/Pop columns
- Inline message row for blocking errors
- Footer actions:
  - Select
  - Cancel

**Behavior**

- Name cells prefix alignment emoji (Face 😃, Heel 😈) and truncate names longer than 18 characters to 15 + `...`
- Stamina, mic skill, and popularity cells show numbers only
- Popularity cells append 🥱 for low stamina and 📅 for booked wrestlers
- Wrestlers already booked in other slots show a 📅 marker
- Wrestlers selected in the current draft also show a 📅 marker
- Selecting an unavailable wrestler shows a ⛔ message and blocks selection

**Blocking rules**

- Cannot select the other side of the current match
- Cannot select already-booked wrestlers
- Wrestlers below `STAMINA_MIN_BOOKABLE` are blocked for matches but allowed for promos

---

### 8.12 Match Type Selection Screen

**Components**

- Match type list
- Description panel
- Footer actions:
  - Select
  - Cancel

**Behavior**

- All match types are selectable
- Highlighting a match type updates the description panel
- No modifiers or numbers are shown

---

### 8.13 Match Booking Confirmation (Modal)

Match booking uses a **modal confirmation dialog**, not a separate screen.

**Purpose**

- Prevent accidental booking commits
- Require explicit confirmation without disrupting context

**Presentation**

- Appears as a small modal overlay on top of the Match Booking screen
- Background screen remains visible but non-interactive
- Focus is trapped inside the modal

**Modal content**

- Single-line prompt: `Confirm booking?`

**Actions**

- `Confirm` – commits the booking and returns to Booking Hub
- `Cancel` / `Esc` – closes the modal and returns to Booking

No match details, stats, or repetition are shown in the modal; full context is already visible underneath.

---

### 8.14 Simulating Show Screen

**Components**

- Static status text
- Optional progress indicator

**Behavior**

- No input accepted
- Calls `GameState.run_show()` on entry
- Automatically advances to Show Results after a short delay

---

### 8.15 Show Results Screen

**Components**

- Slot results list:
  - Matches: Winner vs Loser + match rating (stars only, half-star precision)
  - Promos: Wrestler name + promo rating (stars only)
- Overall show rating (stars only)
- Footer actions:
  - Continue (return to Game Hub)

**Behavior**

- Esc does nothing
- Continue returns to the Game Hub

---

### 8.16 Roster Overview

**Components**

- Wrestler table with Name/Sta/Mic/Pop columns
- Footer action:
  - Back

**Behavior**

- Read-only
- Name cells prefix alignment emoji (Face 😃, Heel 😈) and truncate names longer than 18 characters to 15 + `...`
- Stamina, mic skill, and popularity cells show numbers only
- Popularity cells append 🥱 for low stamina
- List rows are rebuilt on resume to reflect updated show results (no reuse of mounted list item IDs)

---

### 8.17 Widget Mapping (Textual)

| Screen               | Primary Widgets             |
| -------------------- | --------------------------- |
| Main Menu            | ListView, Static, Footer    |
| Game Hub             | ListView, Static, Footer    |
| Booking Hub          | ListView, Static, Button    |
| Match Booking        | ListView, Static, Button    |
| Promo Booking        | ListView, Static, Button    |
| Wrestler Selection   | DataTable, Static, Button   |
| Match Type Selection | ListView, Static, Button    |
| Confirmation         | ModalScreen, Static, Button |
| Simulating           | Static, Footer              |
| Results              | Static, Button, Footer      |
| Roster               | DataTable, Static, Button   |

---

### 8.18 Microcopy & Tone Rules

- Neutral, observational language
- No judgment or advice
- No system explanations
- Use "def." instead of "defeated"
- Stars only for ratings

---

### 8.19 UX Guarantees

- Keyboard-only interaction
- Deterministic behavior
- No accidental exits
- Explicit player intent required for progression

---

### 8.20 ASCII Screen Mockups (Authoritative)

The following ASCII mockups define the **intended visual layout** for all MVP screens after the slot-based booking redesign.

---

#### 8.20.1 Main Menu

```text
┌──────────────────────────────────────┐
│ WrestleGM                            │
│ Main Menu                            │
├──────────────────────────────────────┤
│ ▸ New Game                           │
│                                      │
│   Quit                               │
│                                      │
├──────────────────────────────────────┤
│ ↑↓ Navigate   Enter Select           │
└──────────────────────────────────────┘
```

---

#### 8.20.2 Game Hub

```text
┌──────────────────────────────────────┐
│ WrestleGM                            │
│ Game Hub                             │
├──────────────────────────────────────┤
│ ▸ Book Current Show                  │
│   Show #12                           │
│                                      │
│   Roster Overview                    │
│                                      │
│   Exit to Main Menu                  │
├──────────────────────────────────────┤
│ ↑↓ Navigate   Enter Select   Q Quit  │
└──────────────────────────────────────┘
```

---

#### 8.20.3 Booking Hub (Slot-Level)

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

---

#### 8.20.4 Match Booking (Empty Slot)

```text
┌──────────────────────────────────────┐
│ Book Match 3                         │
├──────────────────────────────────────┤
│ ▸ Wrestler A                         │
│   [ Empty ]                          │
│                                      │
│   Wrestler B                         │
│   [ Empty ]                          │
│                                      │
│   Match Type                         │
│   Singles                            │
│                                      │
├──────────────────────────────────────┤
│ [ Confirm ] (disabled)               │
│ [ Clear Slot ] (disabled)            │
│ [ Cancel ]                           │
└──────────────────────────────────────┘
```

---

#### 8.20.5 Match Booking (Filled Slot)

```text
┌──────────────────────────────────────┐
│ Book Match 3                         │
│ Kenny Omega vs Eddie Kingston        │
├──────────────────────────────────────┤
│ ▸ Wrestler A                         │
│   Kenny Omega            🥱          │
│                                      │
│   Wrestler B                         │
│   Eddie Kingston                     │
│                                      │
│   Match Type                         │
│   Singles                            │
│                                      │
├──────────────────────────────────────┤
│ [ Confirm ]                          │
│ [ Clear Slot ]                       │
│ [ Cancel ]                           │
└──────────────────────────────────────┘
```

---

#### 8.20.6 Promo Booking (Filled Slot)

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

---

#### 8.20.7 Wrestler Selection

Select Wrestler (Match 3 · A)

| Name                 | Sta | Mic | Pop     |
| -------------------- | --- | --- | ------- |
| 😃 Kenny Omega       |  28 |  88 |  92 🥱 📅 |
| 😈 Jon Moxley        |  12 |  86 |  88 🥱   |
| 😃 Eddie Kingston    |  64 |  70 |  74     |

⛔ Already booked in Match 2

[ Select ]   [ Cancel ]

---

#### 8.20.8 Match Type Selection

```text
┌──────────────────────────────────────┐
│ Select Match Type                    │
├──────────────────────────────────────┤
│ ▸ Singles                            │
│   Standard one-on-one contest        │
│                                      │
│   Hardcore                           │
│   No rules. High risk. Brutal.       │
│                                      │
│   Submission                         │
│   Victory by tap-out only            │
├──────────────────────────────────────┤
│ [ Select ]   [ Cancel ]              │
└──────────────────────────────────────┘
```

---

#### 8.20.9 Match Booking Confirmation (Modal)

```text
              ┌──────────────────────┐
              │ Confirm booking?     │
              ├──────────────────────┤
              │ [ Confirm ]          │
              │ [ Cancel ]           │
              └──────────────────────┘
```

---

#### 8.20.10 Show Results

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

---

#### 8.20.11 Roster Overview

Roster Overview

| Name                   | Sta | Mic | Pop  |
| ---------------------- | --- | --- | ---- |
| 😃 Kenny Omega         |  28 |  88 |  89  |
| 😈 Jon Moxley          |  12 |  86 |  82 🥱 |
| 😃 Eddie Kingston      |  64 |  70 |  74  |
| 😃 Claudio Castagnoli  |  71 |  75 |  77  |

[ Back ]

---
