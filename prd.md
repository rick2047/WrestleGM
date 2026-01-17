
---
# FILE: openspec/project.md
---

# Project Context

## Purpose
Create a fun wrestling manager sim where the core enjoyment comes from managing a roster, booking matches, and producing great shows over time.

## Vision & Goals
- Show-driven progression: book, simulate, and advance one show at a time.
- Deterministic but expressive outcomes driven by roster stats and match types.
- Long-term roster evolution is the core reward loop.
- Keyboard-only experience suitable for narrow terminals (target <= 40 columns).
- Systemic, not scripted: outcomes are explained by numbers, not hidden scripts.

Success criterion:
- After multiple shows, the roster and show quality clearly change based on booking decisions.

## Tech Stack
- Python (Textual for UI)
- pytest, ruff, mkdocs
- Minimal third-party dependencies

## Project Conventions

### Code Style
- Prefer clear, Zen-of-Python style implementations
- Use docstrings on modules, classes, and public functions

### Architecture Patterns
- Modular structure with a clear separation between simulation and UI
- Simulation core should be UI-agnostic to allow future UI swaps

### Design Principles
- Show-first design with explicit show boundaries
- Textual-first UI with consistent widget and CSS usage
- Data-driven domain definitions
- Deterministic simulation (same inputs + seed = same results)
- Keyboard-only navigation and no mouse assumptions
- Explicit systems (no hidden scripts or unexplained outcomes)
- Extensible systems with no hardcoded content in the MVP

### Testing Strategy
- Emphasize determinism and consistency in simulation tests
- Cover bounds and regression cases for core simulation rules

### Git Workflow
- Use detailed, descriptive commit messages

## Domain Context
- The game is show-driven: book 3-match cards, simulate, apply deltas, advance

## Important Constraints
- Keep dependencies minimal
- Keep simulation and UI layers separated for future UI migration

## External Dependencies
- None for MVP

---
# FILE: openspec/specs/data/spec.md
---

# data Specification

## Purpose
TBD - created by archiving change add-wrestlegm-mvp. Update Purpose after archive.
## Requirements
### Requirement: Data-driven wrestler definitions
The system SHALL load wrestler definitions from `data/wrestlers.json` with fields `id`, `name`, `alignment`, `popularity`, `stamina`, and `mic_skill`.

#### Scenario: Load roster on startup
- **WHEN** the app starts
- **THEN** it loads all wrestler definitions from `data/wrestlers.json`

### Requirement: Optional wrestler fields
The system SHALL not require optional wrestler fields such as `style`, `tags`, or `injury_status`, and SHALL ignore additional fields not used by the MVP.

#### Scenario: Optional wrestler fields ignored
- **WHEN** wrestler data includes extra fields
- **THEN** the app loads the required fields and ignores the extras

### Requirement: Data-driven match type definitions
The system SHALL load match type definitions from `data/match_types.json` with fields `id`, `name`, `description`, `modifiers`, and optional `allowed_categories`. If `allowed_categories` is omitted, the system SHALL treat the match type as available for all categories.

#### Scenario: Load match types on startup
- **WHEN** the app starts
- **THEN** it loads match type definitions including `allowed_categories`
- **AND THEN** match types missing `allowed_categories` are treated as available for all categories
- **AND THEN** the match types include Standard plus Ambulance, and Ambulance is restricted to Singles

#### Scenario: Match type modifier fields
- **WHEN** match type definitions are loaded
- **THEN** modifiers include outcome_chaos, rating_bonus, rating_variance, stamina_cost_winner, stamina_cost_loser, popularity_delta_winner, and popularity_delta_loser

### Requirement: Match category registry
The system SHALL define a static match category registry with `id`, `name`, and `size` fields for each category, and SHALL include Singles (2), Triple Threat (3), and Fatal 4-Way (4).

#### Scenario: Load match categories
- **WHEN** the app starts
- **THEN** the match category registry includes Singles, Triple Threat, and Fatal 4-Way with the correct sizes

---
# FILE: openspec/specs/game-loop/spec.md
---

# game-loop Specification

## Purpose
TBD - created by archiving change add-wrestlegm-mvp. Update Purpose after archive.
## Requirements
### Requirement: Show-driven progression loop
The system SHALL support a show-driven loop that books a 3-match, 2-promo card, simulates the show via a `SimulationEngine`, applies deltas via a `ShowApplier`, and advances to the next show.

#### Scenario: Complete a show and advance
- **WHEN** the player runs a fully booked show
- **THEN** the system simulates all match and promo slots, applies deltas, and increments the show index

#### Scenario: Core loop sequence
- **WHEN** a new game is started
- **THEN** the player can book the current show, run it, review results, and return to the game hub to advance

#### Scenario: Show results stored
- **WHEN** a show completes simulation
- **THEN** results and the overall show rating are stored on the show

### Requirement: Show model fields
The system SHALL represent a show with `show_index`, `scheduled_slots`, `results`, and `show_rating` fields.

#### Scenario: Show structure
- **WHEN** a show is created
- **THEN** it includes the show index, scheduled slots, results list, and show rating

### Requirement: Match and promo slot fields
The system SHALL represent match slots with `wrestler_ids`, `match_category_id`, and `match_type_id` fields, and promo slots with `wrestler_id`.

#### Scenario: Match slot structure
- **WHEN** a match slot is booked
- **THEN** it records the wrestler ids, match category id, and match type id

#### Scenario: Promo slot structure
- **WHEN** a promo slot is booked
- **THEN** it records the wrestler id

### Requirement: Fixed show slot order
The system SHALL structure each show card as five slots in the fixed order Match 1, Promo 1, Match 2, Promo 2, Match 3.

#### Scenario: Show card slot order
- **WHEN** a new show card is created
- **THEN** it contains five slots in the fixed match/promo order

### Requirement: Fixed show card size
The system SHALL require each show card to contain exactly three matches and two promos.

#### Scenario: Validate show card size
- **WHEN** a show card is validated
- **THEN** it contains exactly three matches and two promos

### Requirement: No slot weighting
The system SHALL not apply weighting or bonuses (e.g., main event bonuses) to slot ratings in the MVP.

#### Scenario: No weighted slots
- **WHEN** the show rating is computed
- **THEN** each slot contributes equally

### Requirement: No card edits during simulation flow
The system SHALL not expose show card editing actions while the simulating or results screens are active.

#### Scenario: Card edits unavailable while simulating
- **WHEN** a show enters simulation
- **THEN** the UI does not offer booking actions until results are complete

### Requirement: Show card reset after completion
The system SHALL clear the show card after a show is completed and applied.

#### Scenario: Reset card after show
- **WHEN** a show is applied and the game advances
- **THEN** the current show card is reset to empty slots

### Requirement: Show validation rules
The system SHALL prevent running a show unless it has exactly three valid matches, two promos each with a wrestler assigned, no duplicate wrestlers across any slot, all match-booked wrestlers meet stamina requirements, each match includes exactly the number of wrestlers required by its selected match category, and each stipulation is allowed for its selected category.

#### Scenario: Block invalid show run
- **WHEN** the card is incomplete, contains duplicate wrestlers, has a match wrestler below stamina requirements, a match does not meet its required category size, or a stipulation is incompatible with its category
- **THEN** the system blocks simulation

### Requirement: Unique wrestler usage per show
The system SHALL prevent a wrestler from appearing in more than one slot on the same show.

#### Scenario: Block duplicate wrestler usage
- **WHEN** a wrestler is already booked in another slot
- **THEN** the show is invalid

### Requirement: Match booking stamina threshold
The system SHALL require wrestlers to have stamina greater than `STAMINA_MIN_BOOKABLE = 10` to be booked in a match.

#### Scenario: Enforce minimum stamina for matches
- **WHEN** a wrestler has stamina of 10 or below
- **THEN** they cannot be booked into a match

### Requirement: Promo stamina exception
The system SHALL allow low-stamina wrestlers to be booked in promo slots.

#### Scenario: Low-stamina promos allowed
- **WHEN** a wrestler is below `STAMINA_MIN_BOOKABLE`
- **THEN** they may still be booked into a promo slot

### Requirement: Between-show recovery
The system SHALL restore stamina to wrestlers who did not participate in the previous show by a fixed amount and clamp to 0–100.

#### Scenario: Resting wrestler recovers stamina
- **WHEN** a wrestler does not appear in any match or promo on the show
- **THEN** their stamina increases by the recovery amount and is clamped to 0–100

#### Scenario: Recovery amount
- **WHEN** recovery is applied
- **THEN** resting wrestlers regain 15 stamina

### Requirement: Recovery timing and determinism
The system SHALL apply recovery after show deltas are applied, before the next show enters planning, and SHALL not use RNG during recovery.

#### Scenario: Recovery timing
- **WHEN** a show completes
- **THEN** recovery is applied after deltas and before the next show is planned

#### Scenario: Recovery uses no RNG
- **WHEN** recovery is applied
- **THEN** no RNG draws occur

### Requirement: Recovery non-rules
The system SHALL not provide partial recovery for participants, rating-based recovery, bonuses for main events, injuries, or time-based simulation between shows in the MVP.

#### Scenario: No extra recovery rules
- **WHEN** recovery is applied
- **THEN** only resting wrestlers receive the fixed recovery amount

### Requirement: Show lifecycle flow
The system SHALL progress through planning, simulating, results, and applied phases via the UI flow without requiring explicit lifecycle state tracking in the data model.

#### Scenario: Show lifecycle flow
- **WHEN** a show is booked and run
- **THEN** the UI follows the planning, simulating, results, and applied phases in order

### Requirement: Ordering guarantees
The system SHALL simulate slots in card order, and the order SHALL not affect outcomes or ratings in the MVP.

#### Scenario: Simulation order is stable
- **WHEN** a show is simulated
- **THEN** slots are processed in card order

### Requirement: Show applier responsibilities
The system SHALL apply match deltas, promo deltas, and between-show recovery through a dedicated `ShowApplier` owned by game state.

#### Scenario: Apply show results through applier
- **WHEN** a show finishes simulation
- **THEN** the `ShowApplier` applies match deltas, promo deltas, recovery, and clamping rules

---
# FILE: openspec/specs/simulation/spec.md
---

# simulation Specification

## Purpose
TBD - created by archiving change add-wrestlegm-mvp. Update Purpose after archive.
## Requirements
### Requirement: Deterministic match simulation pipeline
The system SHALL simulate each match using an outcome step, rating step, and stat delta step using a single seeded RNG instance owned by a `SimulationEngine`, and SHALL support matches with `N` wrestlers where `N >= 2`.

#### Scenario: Deterministic outcomes with same inputs
- **WHEN** the same roster stats, stipulation config, show card, and seed are used for matches with `N >= 2`
- **THEN** the match winners, ratings, and deltas are identical across runs

### Requirement: RNG governance and hidden inputs
The system SHALL use a single seeded RNG for all simulation randomness and SHALL not depend on wall-clock time, UI state, or other implicit inputs.

#### Scenario: No hidden randomness inputs
- **WHEN** the same explicit inputs and seed are used
- **THEN** outcomes are reproducible without relying on hidden inputs

### Requirement: Outcome simulation formula and RNG discipline
The system SHALL compute winners using the outcome pipeline and use exactly one RNG draw per match for the final probability sample.

#### Scenario: Outcome probability and sampling
- **WHEN** a match is simulated with `N` wrestlers
- **THEN** power is computed per wrestler as `power_i = popularity_i * P_WEIGHT + stamina_i * S_WEIGHT`
- **AND THEN** base probabilities are `p_base_i = power_i / sum(power)`
- **AND THEN** if total power is 0, base probabilities are uniform
- **AND THEN** chaos is applied as `p_final_i = lerp(p_base_i, 1/N, outcome_chaos)`
- **AND THEN** the `p_final_i` values are normalized to sum to 1
- **AND THEN** a single RNG draw `r` selects the winner from the cumulative distribution of `p_final_i`

### Requirement: Rating simulation formula and bounds
The system SHALL compute match ratings in 0–100 space, apply a list of rating modifiers (with any star-based bonuses converted to 0–100 using 1 star = 20 points), apply variance using one RNG draw, convert to stars, and clamp to 0.0–5.0 stars.

#### Scenario: Rating computation with modifiers
- **WHEN** a match rating is simulated for `N` wrestlers
- **THEN** `base_100 = pop_avg * POP_W + sta_avg * STA_W` using averages across all wrestlers
- **AND THEN** all registered rating modifiers are applied to the `base_100` rating, including a match type bonus modifier
- **AND THEN** one RNG draw applies `swing` in `[-rating_variance, +rating_variance]`
- **AND THEN** `rating_100` is clamped to 0–100 and converted to stars via `round(rating_100 / 20, 1)`
- **AND THEN** the final rating is clamped to 0.0–5.0 stars

### Requirement: Stat delta simulation rules
The system SHALL produce popularity and stamina deltas based solely on match type modifiers.

#### Scenario: Winner and loser deltas
- **WHEN** a match completes with `N` wrestlers
- **THEN** the winner receives `popularity_delta_winner` and `-stamina_cost_winner` once
- **AND THEN** each non-winner receives `popularity_delta_loser` and `-stamina_cost_loser` once

#### Scenario: Match rating does not alter deltas
- **WHEN** a match rating is computed
- **THEN** popularity and stamina deltas depend only on match type modifiers

#### Scenario: Stamina costs are fixed by match type
- **WHEN** a match is simulated
- **THEN** stamina deltas use the match type stamina costs without scaling by rating

### Requirement: Show rating aggregation
The system SHALL compute the overall show rating as the arithmetic mean of match and promo ratings.

#### Scenario: Aggregate show rating
- **WHEN** a show has slot ratings for matches and promos
- **THEN** the show rating equals their arithmetic mean

#### Scenario: Empty show rating
- **WHEN** a show has no slot ratings
- **THEN** the show rating is `0.0`

#### Scenario: Show rating uses no RNG
- **WHEN** the show rating is computed
- **THEN** no RNG draws are used

### Requirement: End-of-show state application
The system SHALL apply all stat deltas once per show and clamp popularity and stamina to 0–100.

#### Scenario: Clamp stats after applying deltas
- **WHEN** deltas would push a stat below 0 or above 100
- **THEN** the resulting stat is clamped to the 0–100 range

#### Scenario: Apply deltas once per show
- **WHEN** a show completes
- **THEN** all stat deltas are applied once and order does not change results

### Requirement: Between-show stamina recovery
The system SHALL restore stamina only for wrestlers who did not appear on the previous show and clamp results to 0–100.

#### Scenario: Resting wrestler recovery
- **WHEN** a wrestler did not participate in the last show
- **THEN** their stamina increases by `STAMINA_RECOVERY_PER_SHOW` and is clamped to 0–100

### Requirement: Simulation engine ownership
The system SHALL centralize RNG ownership and simulation methods in a `SimulationEngine` class and remove the standalone functional simulation API.

#### Scenario: Simulation runs through engine
- **WHEN** a show is simulated
- **THEN** the `SimulationEngine` is used to compute outcomes, ratings, and deltas

### Requirement: RNG seed stored in game state
The system SHALL store the simulation RNG seed in game state to support reproducibility during a session.

#### Scenario: Seed retention
- **WHEN** a new game is started with a seed
- **THEN** the seed is retained in state for future simulations in the current session

### Requirement: Deterministic promo simulation pipeline
The system SHALL simulate each promo using a rating step and a stat delta step using the same seeded RNG instance owned by a `SimulationEngine`.

#### Scenario: Deterministic promo ratings with same inputs
- **WHEN** the same wrestler stats and seed are used
- **THEN** promo ratings and deltas are identical across runs

### Requirement: Show simulation order
The system SHALL simulate show slots in card order and return results in the same order.

#### Scenario: Preserve card order in results
- **WHEN** a show card is simulated
- **THEN** the results list follows the original slot order

### Requirement: Simulation pipeline stages
The system SHALL run the simulation pipeline in this order: outcome (matches only), rating, stat deltas, show rating aggregation, and end-of-show state application.

#### Scenario: Pipeline order
- **WHEN** a show is simulated and applied
- **THEN** the pipeline stages execute in the defined order

### Requirement: Promo rating simulation formula and bounds
The system SHALL compute promo ratings in 0–100 space from mic skill and popularity, apply variance using one RNG draw with `PROMO_VARIANCE = 8`, clamp, and convert to 0.0–5.0 stars using the shared conversion rules.

#### Scenario: Promo rating computation and clamping
- **WHEN** a promo rating is simulated
- **THEN** `base_100 = mic_skill * 0.7 + popularity * 0.3`
- **AND THEN** one RNG draw applies `swing` in `[-PROMO_VARIANCE, +PROMO_VARIANCE]`
- **AND THEN** `rating_100` is clamped to 0–100 and converted to stars via `round((rating_100/100)*5, 1)`

### Requirement: Promo stat delta rules
The system SHALL apply fixed popularity deltas based on promo quality and grant stamina recovery during promos.

#### Scenario: Promo popularity deltas
- **WHEN** a promo rating is below 50
- **THEN** the wrestler popularity delta is -5
- **AND WHEN** a promo rating is at least 50
- **THEN** the wrestler popularity delta is +5

#### Scenario: Promo stamina recovery
- **WHEN** a wrestler appears in a promo slot
- **THEN** the wrestler stamina delta is `floor(STAMINA_RECOVERY_PER_SHOW / 2)`

### Requirement: Simulation debug payloads
The system SHALL provide debug payloads for outcome, rating, and promo rating simulations that include the intermediate values used to compute results.

#### Scenario: Outcome debug payload
- **WHEN** a match outcome is simulated
- **THEN** the debug payload includes powers, base probabilities, outcome chaos, final probabilities, RNG sample, and winner id

#### Scenario: Rating debug payload
- **WHEN** a match rating is simulated
- **THEN** the debug payload includes averages, alignment modifier, rating bonus, variance, swing, and rating values

#### Scenario: Promo debug payload
- **WHEN** a promo rating is simulated
- **THEN** the debug payload includes base rating, swing, and rating values

### Requirement: Result payloads include deltas and identifiers
The system SHALL include stat deltas in match and promo results, include applied match type modifiers on match results, and record winner/non-winners, rating, match category, and match type identifiers.

#### Scenario: Match result payload
- **WHEN** a match is simulated
- **THEN** the result includes winner id, non-winner ids, rating, match category id, match type id, applied modifiers, and stat deltas

#### Scenario: Promo result payload
- **WHEN** a promo is simulated
- **THEN** the result includes wrestler id, rating, and stat deltas

### Requirement: Simulation test coverage
The system SHALL include tests that cover determinism, outcome normalization, rating bounds, alignment modifiers, multi-man determinism, promo determinism, promo deltas, match deltas, show rating aggregation, and stat clamping.

#### Scenario: Simulation tests run
- **WHEN** simulation tests run
- **THEN** they cover determinism, outcome, rating bounds, alignment, multi-man, promo, deltas, show rating, and clamp behavior

### Requirement: Extensible rating modifier system
The system SHALL provide a `RatingModifier` interface that allows for the creation of new rating adjustment logic without modifying the core simulation engine.

#### Scenario: Alignment modifier
- **WHEN** a match is simulated with a `AlignmentModifier`
- **THEN** for 1v1 matches, the modifier returns `+ALIGN_BONUS` for face vs heel, `-2 * ALIGN_BONUS` for heel vs heel, and `0` for face vs face
- **AND THEN** for matches with `N >= 3`, the modifier returns `-2 * ALIGN_BONUS` for all heels, `0` for all faces, `+ALIGN_BONUS` for heels > faces, `0` for heels == faces, and `-ALIGN_BONUS` for faces > heels

#### Scenario: Rivalry modifier
- **WHEN** a match is simulated with a `RivalryModifier`
- **THEN** each active rivalry pair adds a configurable bonus (defined in stars and converted to 0–100 by multiplying by 20)
- **AND THEN** each blowoff pair adds a configurable bonus (defined in stars and converted to 0–100 by multiplying by 20)

#### Scenario: Cooldown modifier
- **WHEN** a match is simulated with a `CooldownModifier`
- **THEN** if any cooldown pair exists in the match, a configurable penalty (defined in stars and converted to 0–100 by multiplying by 20) is applied to the rating

---
# FILE: openspec/specs/ui/spec.md
---

# ui Specification

## Purpose
TBD - created by archiving change add-wrestlegm-mvp. Update Purpose after archive.
## Requirements
### Requirement: Textual MVP screens
The system SHALL provide the MVP screens defined in the PRD using Textual widgets and keyboard-only navigation. The roster screen SHALL read from the session roster stored in `GameState`, render the roster in a table with Name/Stamina/Mic/Popularity columns, include a header row naming the name/stamina/mic/popularity columns, format rows as `{emoji} {name:<18} {sta:>3} {mic:>3} {pop:>3}{fatigue}`, display alignment via emoji (Face 😃, Heel 😈), truncate names longer than 18 characters to 15 + `...`, and rebuild its list rows on resume without reusing mounted widget IDs.

#### Scenario: Navigate from main menu to game hub
- **WHEN** the player selects New Game on the main menu
- **THEN** the game hub screen is shown

#### Scenario: Roster refresh after resume
- **WHEN** the user returns to the roster screen after leaving it
- **THEN** the roster list is rebuilt from the session roster without duplicate widget IDs

#### Scenario: Roster header and row formatting
- **WHEN** the roster screen renders
- **THEN** a header row names the name, stamina, mic, and popularity columns
- **AND THEN** each roster row follows the format `{emoji} {name:<18} {sta:>3} {mic:>3} {pop:>3}{fatigue}`
- **AND THEN** wrestler names longer than 18 characters are truncated to 15 + `...`

#### Scenario: Roster alignment emoji mapping
- **WHEN** the roster screen renders
- **THEN** Face alignment uses 😃 and Heel alignment uses 😈

### Requirement: Global navigation keys and footer
The system SHALL use keyboard-only navigation and display a persistent footer that shows key bindings only. Enter SHALL activate the focused widget. Escape SHALL back out of the current screen or modal where a back action exists, except on the Game Hub, Main Menu, and Show Results screens where Escape has no effect. Arrow-key focus order SHALL skip disabled action buttons, loop between lists and action buttons, and wrap from last to first and first to last within a screen. Left/Right keys SHALL move between horizontal fields or buttons where applicable.

#### Scenario: Footer visibility
- **WHEN** any screen is shown
- **THEN** the footer is visible and displays only key bindings

#### Scenario: Arrow-key navigation across actions
- **WHEN** the user presses arrow keys on booking hub, match booking, results, or roster
- **THEN** focus can move from list views to the action buttons and back in a cycle

#### Scenario: Left/right navigation across buttons
- **WHEN** the user presses Left/Right on a screen with horizontal buttons
- **THEN** focus moves between those buttons

#### Scenario: Escape on Game Hub
- **WHEN** the player presses Escape on the Game Hub
- **THEN** no navigation occurs

#### Scenario: Escape on Main Menu
- **WHEN** the player presses Escape on the Main Menu
- **THEN** no navigation occurs

#### Scenario: Escape on Show Results
- **WHEN** the player presses Escape on the Show Results screen
- **THEN** no navigation occurs

### Requirement: Navigation stack behavior
The system SHALL push and pop screens on a navigation stack, pop on Escape where allowed, and preserve in-progress booking drafts while navigating into sub-screens.

#### Scenario: Escape pops the current screen
- **WHEN** the player presses Escape on a screen with a back action
- **THEN** the current screen is popped

#### Scenario: Subscreen selection returns
- **WHEN** the player selects a wrestler or match category
- **THEN** the selection screen is popped and control returns to the parent screen

#### Scenario: Draft state persists across subscreens
- **WHEN** the player opens wrestler selection or match category selection during booking
- **THEN** the in-progress draft remains intact when returning to booking

#### Scenario: Cancel discards draft
- **WHEN** the player cancels a booking screen
- **THEN** the in-progress draft is discarded without committing changes

### Requirement: Footer behavior
The system SHALL render a footer on all screens that displays key bindings only, updates based on focus, shows only modal bindings when a modal is open, and hides internal or non-action bindings.

#### Scenario: Footer shows key bindings only
- **WHEN** any screen is visible
- **THEN** the footer shows key bindings only and no game state or hints

#### Scenario: Footer is authoritative
- **WHEN** the player needs to discover available actions
- **THEN** the footer reflects the current available key bindings

#### Scenario: Footer updates for modals
- **WHEN** a modal is open
- **THEN** the footer shows only modal bindings

#### Scenario: Hidden bindings are excluded
- **WHEN** internal bindings exist
- **THEN** they do not appear in the footer

### Requirement: Visual indicator language
The system SHALL use a consistent emoji indicator language and alignment emojis in roster and booking views.

| Indicator | Meaning                                         | Blocks Action |
| --------- | ----------------------------------------------- | ------------- |
| ⛔         | Logical impossibility (e.g. duplicate wrestler) | Yes           |
| 🥱        | Low stamina / fatigued                          | Yes           |
| 📅        | Already booked in another slot                  | Yes           |

Alignment SHALL be shown by prefixing the wrestler name with Face 😃 or Heel 😈. Indicators rely on iconography first; color is supplemental.

#### Scenario: Alignment emoji usage
- **WHEN** wrestler names are rendered in roster or booking lists
- **THEN** they are prefixed with 😃 for Face and 😈 for Heel

#### Scenario: Blocked actions show ⛔
- **WHEN** an invalid selection is attempted
- **THEN** the UI displays a ⛔ indicator with a short inline message

#### Scenario: Empty slots show placeholders
- **WHEN** a booking field is empty or incomplete
- **THEN** it shows an `[ Empty ]` or `[ Unset ]` placeholder and the action is blocked

### Requirement: Validation philosophy
The system SHALL validate actions at commit time, block impossible states only, allow low-stamina wrestlers in promos, avoid advisory warnings beyond indicators and short inline errors, and avoid projections or odds in the UI.

#### Scenario: Block impossible states only
- **WHEN** a selection would create a duplicate or invalid booking
- **THEN** the UI blocks the action and shows the corresponding indicator

#### Scenario: No projections or advice
- **WHEN** the player is booking or reviewing results
- **THEN** the UI does not display odds, projections, or advisory hints

### Requirement: Booking hub behavior
The system SHALL show five slots in fixed order (Match 1, Promo 1, Match 2, Promo 2, Match 3), allow slot selection, show match participant names with alignment emoji, show `Category · Stipulation` for match slots, and enable Run Show only when all slots are booked.

#### Scenario: Run Show enablement
- **WHEN** any slot is empty
- **THEN** Run Show is disabled

#### Scenario: Run Show requires a valid card
- **WHEN** the show card has validation errors
- **THEN** Run Show is disabled

#### Scenario: Show category and type for matches
- **WHEN** the booking hub renders a booked match
- **THEN** it shows a `Category · Stipulation` line under the participant list

#### Scenario: Match participants display format
- **WHEN** a match slot is booked
- **THEN** the participant line uses alignment emojis and separates names with `vs`

#### Scenario: Enter opens slot editor
- **WHEN** the player selects a match slot
- **THEN** the match category selection screen opens

- **WHEN** the player selects a promo slot
- **THEN** the promo booking screen opens

#### Scenario: No partial slots on the card
- **WHEN** a slot is shown as booked in the booking hub
- **THEN** it contains a fully valid match or promo

#### Scenario: Back returns to Game Hub
- **WHEN** the player selects Back on the booking hub
- **THEN** the Game Hub is shown

### Requirement: Match booking flow
The system SHALL edit matches in a dedicated booking screen, require confirmation before committing, and split match category selection (size) from stipulation selection (rules). The booking screen SHALL open after a category is chosen, render one wrestler row per required slot based on category, filter stipulations to those allowed for the selected category, allow changing stipulation via an inline dropdown, default the stipulation to the first available option when booking an empty slot, mark already-booked wrestlers with a 📅 indicator in the selection list, show popularity and stamina, display alignment via emoji (Face 😃, Heel 😈), render the selection list as a table with Name/Stamina/Mic/Popularity columns, include a header row naming the name/stamina/mic/popularity columns, truncate names longer than 18 characters to 15 + `...`, format rows as `{emoji} {name:<18} {sta:>3} {mic:>3} {pop:>3}{fatigue}{booked_marker}`, and use 🥱 consistently for low-stamina indicators.

#### Scenario: Stipulation dropdown opens on Enter
- **WHEN** the user focuses the stipulation dropdown in match booking
- **AND WHEN** they press Enter
- **THEN** the stipulation dropdown opens without error

#### Scenario: Match booking opens after category selection
- **WHEN** the player selects a match category
- **THEN** match booking opens for that slot

#### Scenario: Re-selecting a match category keeps early picks
- **WHEN** the player re-selects a match category with fewer required slots
- **THEN** the earliest selected wrestlers remain assigned and any extra slots are cleared

#### Scenario: Re-selecting a match category adds new slots
- **WHEN** the player re-selects a match category with more required slots
- **THEN** the existing selected wrestlers remain assigned and new empty slots are added

#### Scenario: Confirm disabled until valid
- **WHEN** the match booking screen has incomplete or invalid selections
- **THEN** the Confirm action is disabled

#### Scenario: Clear Slot availability
- **WHEN** the match slot is empty
- **THEN** Clear Slot is disabled

#### Scenario: Cancel returns to match category selection
- **WHEN** the player selects Cancel or presses Escape in match booking
- **THEN** they return to match category selection without committing changes

#### Scenario: Draft selections show booked marker
- **WHEN** the wrestler selection screen is opened during match booking
- **THEN** wrestlers already selected in the current draft show a 📅 marker

#### Scenario: Clear Slot returns to booking hub
- **WHEN** the player clears a booked match slot
- **THEN** the slot is emptied and the booking hub is shown

#### Scenario: Stipulation list filters by category
- **WHEN** a match category is selected
- **THEN** the stipulation list includes only stipulations allowed for that category

#### Scenario: Default stipulation for empty slots
- **WHEN** the player books an empty match slot
- **THEN** the stipulation defaults to the first available option

### Requirement: Match booking confirmation modal
The system SHALL confirm match booking via a modal overlay with the prompt `Confirm booking?`, explicit Confirm/Cancel actions, and trapped focus.

#### Scenario: Confirmation modal prompt
- **WHEN** the confirmation modal is displayed
- **THEN** it shows the prompt `Confirm booking?`

#### Scenario: Confirmation modal focus trap
- **WHEN** the confirmation modal is open
- **THEN** focus is trapped inside the modal and the background is non-interactive

### Requirement: Booking validation in UI
The system SHALL block committing invalid matches and running invalid shows according to the booking rules.

#### Scenario: Prevent duplicate wrestler booking
- **WHEN** a wrestler is already booked in another slot
- **THEN** the UI marks them with a 📅 indicator and prevents selection with a ⛔ message

#### Scenario: Allow low-stamina promos
- **WHEN** a wrestler has stamina below `STAMINA_MIN_BOOKABLE`
- **THEN** the UI still allows selecting them for a promo slot

#### Scenario: Block low-stamina match booking
- **WHEN** a wrestler has stamina at or below `STAMINA_MIN_BOOKABLE` and the player is booking a match
- **THEN** the UI prevents selection with a ⛔ message

#### Scenario: Prevent partial slot commits
- **WHEN** required booking fields are incomplete
- **THEN** the UI prevents committing the slot

#### Scenario: Prevent duplicates within a match
- **WHEN** the player selects a wrestler already chosen in the same match
- **THEN** the UI blocks the selection with a ⛔ message

### Requirement: Results presentation
The system SHALL present match and promo results and the overall show rating using star ratings only with half-star precision, and SHALL include `Category · Stipulation` for match results.

#### Scenario: Show results after simulation
- **WHEN** the show completes
- **THEN** results list match winners and non-winners with star ratings, plus the overall show rating
- **AND THEN** match results include a `Category · Stipulation` line under the participants

### Requirement: Arrow-key navigation consistency
The system SHALL provide cyclical arrow-key navigation across all screens with focusable lists or action buttons.

#### Scenario: Cyclical focus traversal
- **WHEN** the user presses arrow keys on any screen with focusable lists or buttons
- **THEN** focus cycles from the last element back to the first and from the first back to the last

### Requirement: Main menu meta-only navigation
The system SHALL render a Main Menu that only offers New Game and Quit, and SHALL not expose gameplay screens while a session is active.

### Requirement: MVP screen list
The system SHALL provide the following MVP screens: Main Menu, Game Hub, Booking Hub, Match Booking, Promo Booking, Wrestler Selection, Match Category Selection, Match Confirmation modal, Simulating Show, Show Results, and Roster Overview.

#### Scenario: MVP screens are available
- **WHEN** the player navigates through the UI
- **THEN** each MVP screen is reachable via its expected flow

#### Scenario: Main menu mockup layout
- **WHEN** the Main Menu is displayed
- **THEN** it matches the Main Menu mockup in the ASCII mockups section

#### Scenario: Main menu options
- **WHEN** the Main Menu is shown
- **THEN** the only options are New Game and Quit

#### Scenario: Quit from Main Menu
- **WHEN** the player presses Q on the Main Menu
- **THEN** the application quits

#### Scenario: Enter session from Main Menu
- **WHEN** the player selects New Game
- **THEN** a new session is initialized and the Game Hub is shown

### Requirement: Game hub screen
The system SHALL provide a Game Hub screen that displays the current show number and offers Book Current Show, Roster Overview, and Exit to Main Menu actions. The hub SHALL be the only gateway to gameplay screens and SHALL not run simulation or apply state changes. The show subtitle line under Book Current Show SHALL display the show name/number and be non-selectable text.

#### Scenario: Game hub mockup layout
- **WHEN** the Game Hub is displayed
- **THEN** it matches the Game Hub mockup in the ASCII mockups section

#### Scenario: Show subtitle is descriptive
- **WHEN** the Game Hub is displayed
- **THEN** the show subtitle line is descriptive text and not a separate action

#### Scenario: Quit from Game Hub
- **WHEN** the player presses Q on the Game Hub
- **THEN** the application quits

#### Scenario: Enter hub after new game
- **WHEN** a new session is initialized
- **THEN** the Game Hub is shown with the current show number

#### Scenario: Navigate to booking from hub
- **WHEN** the player selects Book Current Show in the Game Hub
- **THEN** the booking hub screen is shown

#### Scenario: Navigate to roster from hub
- **WHEN** the player selects Roster Overview in the Game Hub
- **THEN** the roster screen is shown

#### Scenario: Exit to Main Menu from hub
- **WHEN** the player selects Exit to Main Menu in the Game Hub
- **THEN** the session ends and the Main Menu is shown

### Requirement: Results return to hub
The system SHALL return to the Game Hub after results and SHALL not provide roster or main menu shortcuts on the results screen.

#### Scenario: Continue after results
- **WHEN** the player selects Continue on the results screen
- **THEN** the Game Hub is shown

### Requirement: Simulating screen behavior
The system SHALL present a Simulating screen that runs `GameState.run_show()` on entry, accepts no input, and automatically advances to the Results screen after a short delay.

#### Scenario: Simulate and advance
- **WHEN** the Simulating screen is shown
- **THEN** the show is run and the Results screen appears automatically

#### Scenario: Simulating screen ignores input
- **WHEN** the Simulating screen is active
- **THEN** user input is ignored

### Requirement: Promo booking flow
The system SHALL provide a promo booking screen that edits a single wrestler for a promo slot and requires confirmation before committing.

#### Scenario: Empty promo slot booking
- **WHEN** the user opens promo booking for an empty slot
- **THEN** the screen shows a single Wrestler field and a disabled Confirm action

#### Scenario: Promo wrestler field opens selection
- **WHEN** the player activates the Wrestler field
- **THEN** the wrestler selection screen opens

#### Scenario: Confirm promo booking
- **WHEN** the user selects Confirm with a valid wrestler selected
- **THEN** a confirmation modal prompts for final confirmation before saving the slot

#### Scenario: Clear Slot availability for promos
- **WHEN** the promo slot is empty
- **THEN** Clear Slot is disabled

#### Scenario: Clear promo returns to booking hub
- **WHEN** the player clears a booked promo slot
- **THEN** the slot is emptied and the booking hub is shown

#### Scenario: Cancel promo booking
- **WHEN** the player cancels promo booking
- **THEN** changes are discarded and the booking hub is shown

### Requirement: Shared wrestler selection for promos
The system SHALL reuse the existing wrestler selection screen for promo booking and may change only the contextual title text and validation rules needed to allow low-stamina promo selection.

#### Scenario: Promo wrestler selection layout
- **WHEN** the user opens wrestler selection from promo booking
- **THEN** the table layout, columns, and indicators match the match-booking selection screen

### Requirement: Wrestler selection screen layout
The system SHALL render a wrestler selection table with Name/Sta/Mic/Pop columns, an inline message row for blocking errors, and Select/Cancel actions.

#### Scenario: Wrestler selection components
- **WHEN** the wrestler selection screen renders
- **THEN** it shows the table, inline message row, and Select/Cancel actions

### Requirement: Mic skill visibility in roster and selection
The system SHALL display wrestler mic skill on the roster overview and wrestler selection screens using the same table layout.

#### Scenario: Mic skill column shown
- **WHEN** the roster overview or wrestler selection screen renders
- **THEN** the table includes a Mic column showing each wrestler's mic skill value

### Requirement: Match category selection screen
The system SHALL provide a match category selection screen when booking a match slot and use the selected category to determine the required wrestler count in match booking.

#### Scenario: Match category selection
- **WHEN** the user selects a match slot on the booking hub
- **THEN** the match category selection screen lists Singles, Triple Threat, and Fatal 4-Way
- **AND THEN** selecting a match category opens match booking for that slot

#### Scenario: Match category actions
- **WHEN** the match category selection screen is shown
- **THEN** Select and Cancel actions are available

### Requirement: Rivalry and cooldown emoji display
The system SHALL display rivalry and cooldown emojis on the match name line in the Booking Hub and Match Booking screens using the specified emoji mappings, and SHALL update the emoji list live as wrestlers are added or removed.

#### Scenario: Booking hub emojis
- **WHEN** a match slot is rendered in the Booking Hub
- **THEN** rivalry and cooldown emojis appear on the same line as the match name

#### Scenario: Match booking emojis
- **WHEN** the match booking screen has at least two wrestlers selected
- **THEN** rivalry and cooldown emojis appear on the match name line and update as selections change

### Requirement: Rivalry and cooldown emoji mapping and order
The system SHALL map rivalry levels to ⚡, 🔥, ⚔️, and 💥 for levels 1–4 respectively, map cooldown remaining shows to 🧊 (6–5), ❄️ (4–3), and 💧 (2–1), and order emojis by wrestler pair order derived from the booked wrestler list.

#### Scenario: Emoji mapping and ordering
- **WHEN** a match includes multiple rivalry or cooldown pairs
- **THEN** emojis are ordered by the unique pair order derived from the match wrestler list
- **AND THEN** each emoji uses the correct mapping for the pair's rivalry level or cooldown remaining shows

### Requirement: No rivalry emojis in show results
The system SHALL not display rivalry or cooldown emojis on the Show Results screen.

#### Scenario: Results omit rivalry emojis
- **WHEN** the Show Results screen renders
- **THEN** no rivalry or cooldown emojis are shown

### Requirement: Microcopy and tone rules
The system SHALL use neutral, observational language, avoid system explanations or advice, and use "def." instead of "defeated" in match results.

#### Scenario: Match results use "def."
- **WHEN** match results are shown
- **THEN** the winner line uses "def."

### Requirement: UX guarantees
The system SHALL provide keyboard-only interaction, deterministic behavior, no accidental exits, and require explicit player intent for progression.

#### Scenario: No accidental exits
- **WHEN** the player presses Escape on screens without a back action
- **THEN** no navigation occurs

### Requirement: Widget mapping
The system SHALL map each screen to the following primary Textual widgets.

| Screen               | Primary Widgets             |
| -------------------- | --------------------------- |
| Main Menu            | ListView, Static, Footer    |
| Game Hub             | ListView, Static, Footer    |
| Booking Hub          | ListView, Static, Button    |
| Match Booking        | ListView, Select, Static, Button |
| Promo Booking        | ListView, Static, Button    |
| Wrestler Selection   | DataTable, Static, Button   |
| Match Category Selection | ListView, Static, Button    |
| Confirmation         | ModalScreen, Static, Button |
| Simulating           | Static, Footer              |
| Results              | Static, Button, Footer      |
| Roster               | DataTable, Static, Button   |

#### Scenario: Widget usage
- **WHEN** a screen is implemented
- **THEN** it uses the primary widgets listed for that screen

### Requirement: ASCII mockups
The system SHALL match the following ASCII mockups for the MVP screens.

#### Scenario: Screen layouts follow mockups
- **WHEN** an MVP screen is displayed
- **THEN** it matches the corresponding ASCII mockup

#### Main Menu
```
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

#### Game Hub
```
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

#### Booking Hub (Slot-Level)
```
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
│   😈 Jon Moxley vs 😃 Claudio vs 😃 Kenny │
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

#### Match Booking (Empty Slot)
```
┌──────────────────────────────────────┐
│ Book Match 3                         │
│ Singles                              │
├──────────────────────────────────────┤
│ ▸ [ Empty ]                          │
│                                      │
│   [ Empty ]                          │
│                                      │
│   Stipulation                        │
│   [ Hardcore ▾ ]                     │
│                                      │
├──────────────────────────────────────┤
│ [ Confirm ] (disabled)               │
│ [ Clear Slot ] (disabled)            │
│ [ Cancel ]                           │
└──────────────────────────────────────┘
```

#### Match Booking (Filled Slot)
```
┌──────────────────────────────────────┐
│ Book Match 3                         │
│ Singles                              │
├──────────────────────────────────────┤
│ ▸ 😃 Kenny Omega                     │
│                                      │
│   😈 Eddie Kingston                  │
│                                      │
│   Stipulation                        │
│   Submission                         │
│                                      │
├──────────────────────────────────────┤
│ [ Confirm ]                          │
│ [ Clear Slot ]                       │
│ [ Cancel ]                           │
└──────────────────────────────────────┘
```

#### Promo Booking (Filled Slot)
```
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

#### Wrestler Selection
```
Select Wrestler (Match 3 · A)

| Name                 | Sta | Mic | Pop |
| -------------------- | --- | --- | ---:|
| 😃 Kenny Omega       |  28 |  88 |  92 🥱 📅 |
| 😈 Jon Moxley        |  12 |  86 |  88 🥱   |
| 😃 Eddie Kingston    |  64 |  70 |  74     |

⛔ Already booked in Match 2

[ Select ]   [ Cancel ]
```

#### Match Category Selection
```
┌──────────────────────────────────────┐
│ Select Match Category                │
├──────────────────────────────────────┤
│ ▸ Singles                            │
│                                      │
│   Triple Threat                      │
│                                      │
│   Fatal 4-Way                        │
├──────────────────────────────────────┤
│ [ Select ]   [ Cancel ]              │
└──────────────────────────────────────┘
```

#### Match Booking Confirmation (Modal)
```
              ┌──────────────────────┐
              │ Confirm booking?     │
              ├──────────────────────┤
              │ [ Confirm ]          │
              │ [ Cancel ]           │
              └──────────────────────┘
```

#### Show Results
```
┌────────────────────────── SHOW RESULTS ──────────────────────────┐
│ WrestleGM                                                        │
│ Show #12 · RAW                                                   │
├──────────────────────────────────────────────────────────────────┤
│ Match 1                                                         │
│ 😃 Kenny Omega def. 😈 Eddie Kingston                            │
│ Singles · Hardcore                                               │
│                                                          ★★★☆☆ │
│                                                                  │
│ Promo 1                                                         │
│ Jon Moxley                                                      │
│                                                          ★★☆☆☆ │
│                                                                  │
│ Match 2                                                         │
│ 😈 Jon Moxley def. 😃 Claudio Castagnoli                          │
│ Singles · Submission                                             │
│                                                          ★★★★☆ │
│                                                                  │
│ Promo 2                                                         │
│ Maria Blaze                                                     │
│                                                          ★★☆☆☆ │
│                                                                  │
│ Match 3                                                         │
│ 😃 Alpha def. 😈 Beta, 😃 Gamma                                   │
│ Triple Threat · High Flying                                      │
│                                                          ★★★☆☆ │
├──────────────────────────────────────────────────────────────────┤
│ Show Rating: ★★★½☆                                             │
│                                                                  │
│ [ Continue ]                                                    │
└──────────────────────────────────────────────────────────────────┘
```

#### Roster Overview
```
Roster Overview

| Name                   | Sta | Mic | Pop |
| ---------------------- | --- | --- | ---:|
| 😃 Kenny Omega         |  28 |  88 |  89  |
| 😈 Jon Moxley          |  12 |  86 |  82 🥱 |
| 😃 Eddie Kingston      |  64 |  70 |  74  |
| 😃 Claudio Castagnoli  |  71 |  75 |  77  |

[ Back ]
```

---
# FILE: openspec/specs/ui-testing/spec.md
---

# ui-testing Specification

## Purpose
TBD - created by archiving change add-ui-testing. Update Purpose after archive.
## Requirements
### Requirement: Textual UI test harness
The system SHALL provide a Textual UI test harness that uses Textual test utilities to drive keyboard-only interactions in a deterministic environment.

#### Scenario: Deterministic UI test setup
- **WHEN** UI tests run
- **THEN** they use a fixed RNG seed of 2047
- **AND THEN** they use a fixed viewport size of 100x30

### Requirement: UI test fixtures
The system SHALL provide dedicated UI test fixtures for roster and match type inputs to ensure deterministic flows and snapshots.

#### Scenario: Fixture-based UI data
- **WHEN** UI tests run
- **THEN** they load roster and match type data from `tests/fixtures/ui/`

### Requirement: UI flow tests
The system SHALL include UI flow tests that validate keyboard-only navigation and state progression across core gameplay screens.

#### Scenario: Flow coverage for core gameplay
- **WHEN** UI flow tests run
- **THEN** they cover at least the following journeys:
  - New Game -> Game Hub
  - Game Hub -> Booking Hub -> Back -> Game Hub
  - Booking Hub -> Match Booking -> Select Wrestler A + B + Type -> Confirm -> Booking Hub
  - Booking Hub -> Run Show (after all slots booked) -> Results -> Continue -> Game Hub
  - Game Hub -> Roster Overview -> Back

### Requirement: UI snapshot tests
The system SHALL generate deterministic SVG snapshots for canonical UI screens and stable end states only using `pytest-textual-snapshot`.

#### Scenario: Canonical snapshot registry
- **WHEN** snapshot tests run
- **THEN** the snapshot registry is fixed to the following list:
  - S1 Main Menu (default)
  - S2 Game Hub (default)
  - S3 Booking Hub (all slots empty)
  - S4 Booking Hub (all slots filled)
  - S5 Match Booking (empty slot)
  - S6 Match Booking (filled slot)
  - S7 Wrestler Selection (default)
  - S8 Match Type Selection (default)
  - S9 Match Booking Confirmation (modal visible)
  - S10 Show Results (default)
  - S11 Roster Overview (default)

### Requirement: Snapshot baseline management
The system SHALL store SVG snapshot baselines in-repo using the `pytest-textual-snapshot` naming conventions.

#### Scenario: Baseline location and naming
- **WHEN** baselines are committed
- **THEN** they live under `tests/snapshots/`
- **AND THEN** filenames are derived from snapshot test function names and stored with the `.raw` extension

### Requirement: Snapshot enforcement
The system SHALL fail tests when snapshot output does not match baselines.

#### Scenario: Snapshot mismatch handling
- **WHEN** a generated snapshot differs from its baseline
- **THEN** the test run fails


---
# FILE: openspec/specs/documentation/spec.md
---

# documentation Specification

## Purpose
TBD - created by archiving change add-docs-site. Update Purpose after archive.
## Requirements
### Requirement: Documentation site structure
The documentation site SHALL provide dedicated pages for architecture, simulation, UI flows, and implementation reference, plus an API reference generated from docstrings.

#### Scenario: Navigate core documentation
- **WHEN** the user opens the documentation site
- **THEN** they can access pages for architecture, simulation, UI, implementation reference, and API reference via the navigation

### Requirement: API reference from docstrings
The documentation site SHALL include an API reference generated from Python docstrings for the `wrestlegm` package.

#### Scenario: View API reference
- **WHEN** the user opens the API reference page
- **THEN** the page renders module, class, and function documentation from `wrestlegm` docstrings

### Requirement: Textual UI flow documentation
The documentation site SHALL describe the Textual UI screens, navigation flow, and component composition for each screen.

#### Scenario: Review UI flow details
- **WHEN** the user reads the UI documentation
- **THEN** they see each screen's purpose, key bindings, navigation behavior, and main Textual components

### Requirement: API reference grouped by domain
The documentation site SHALL group API reference content into domain sections for simulation, UI, data/state, and constants/models.

#### Scenario: Browse grouped API reference
- **WHEN** the user opens the API reference
- **THEN** module documentation appears under domain section headers

### Requirement: Comprehensive public function docstrings
The codebase SHALL provide docstrings for all public functions to support API reference generation.

#### Scenario: Render function documentation
- **WHEN** the API reference is generated
- **THEN** each public function is documented by its docstring

### Requirement: Documentation accuracy
The documentation SHALL describe the current simulation architecture, including `SimulationEngine` ownership of RNG, `ShowApplier` state mutation, and how `GameState.run_show()` coordinates the pipeline. The documentation SHALL also reflect current UI navigation behavior, implementation ownership details, and command-line usage for running the app, tests, and docs.

#### Scenario: Simulation doc accuracy
- **WHEN** a reader views the simulation documentation
- **THEN** it describes the engine-based pipeline and state application flow used in the current implementation

#### Scenario: UI and implementation doc accuracy
- **WHEN** a reader views the UI or implementation documentation
- **THEN** it reflects current navigation behavior, component focus rules, and ownership boundaries

#### Scenario: Command-line usage accuracy
- **WHEN** a reader views the documentation index
- **THEN** it lists `uv` commands for running the app, tests, and docs

#### Scenario: Documentation build commands
- **WHEN** a reader views documentation build instructions
- **THEN** they see `uv run mkdocs serve` and `uv run mkdocs build`

#### Scenario: App and test commands
- **WHEN** a reader views run/test instructions
- **THEN** they see `uv run main.py` and `uv run pytest`

### Requirement: UI testing documentation
The system SHALL document the UI testing strategy in the `docs/` site, including flow tests, snapshot tests, and how to update baselines.

#### Scenario: Document UI test strategy
- **WHEN** a contributor reads the docs
- **THEN** they can find the UI testing strategy and snapshot update steps in `docs/`

#### Scenario: Snapshot update command documented
- **WHEN** a contributor reads the UI testing docs
- **THEN** they see the command to update snapshots

#### Scenario: Snapshot baseline location documented
- **WHEN** a contributor reads the UI testing docs
- **THEN** they see where snapshot baselines are stored

---
# FILE: openspec/specs/ci/spec.md
---

# ci Specification

## Purpose
TBD - created by archiving change add-pr-ci. Update Purpose after archive.
## Requirements
### Requirement: PR test workflow
The system SHALL run automated tests via `uv run pytest` for every pull request.

#### Scenario: Pull request test run
- **WHEN** a pull request is opened or updated
- **THEN** the workflow runs `uv run pytest` and reports the outcome

### Requirement: Sticky PR test comment
The system SHALL publish a single sticky PR comment with the latest test outcome and update it on each workflow run.

#### Scenario: Update PR test comment
- **WHEN** the PR test workflow completes
- **THEN** the existing test comment is updated with the new result

### Requirement: Detailed test listing
The system SHALL include a detailed list of collected tests in the PR comment, grouped by test class, with emoji-only status indicators per test and reasons for skipped or error cases. Each group SHALL render as a table inside a collapsible section. The emoji mapping SHALL be `✅` for passed, `❌` for failed, `🛑` for error, and `⚠️` for skipped.

#### Scenario: Report test details
- **WHEN** the PR test workflow completes
- **THEN** the PR comment lists test cases grouped by class with per-test status and skip/error reasons in a table

### Requirement: Workflow permissions
The workflow SHALL request only the permissions needed to read code and update PR comments.

#### Scenario: Minimal token access
- **WHEN** the workflow runs
- **THEN** it uses read access for repository contents and write access for PR comments

### Requirement: PR test path filters
The system SHALL run PR tests only when relevant files change: `tests/**`, `wrestlegm/**`, `data/**`, `main.py`, `pyproject.toml`, `uv.lock`, or `.github/workflows/pr-tests.yml`.

#### Scenario: Skip PR tests on unrelated changes
- **WHEN** a pull request changes files outside the relevant paths
- **THEN** the PR test workflow does not run

### Requirement: UI test execution order
The system SHALL run UI flow tests before UI snapshot tests and SHALL only run UI snapshots if prior stages pass.

#### Scenario: Gated UI snapshot run
- **WHEN** simulation or UI flow tests fail
- **THEN** UI snapshot tests do not run

#### Scenario: Separate CI jobs with dependencies
- **WHEN** the CI workflow runs
- **THEN** UI snapshot tests are executed in a separate job that depends on successful completion of simulation and UI flow test jobs

### Requirement: Snapshot artifact upload
The system SHALL upload snapshot diff artifacts produced by `pytest-textual-snapshot` when snapshot tests fail.

#### Scenario: Artifact on snapshot failure
- **WHEN** a UI snapshot test fails
- **THEN** the workflow uploads the snapshot report directory configured via `TEXTUAL_SNAPSHOT_TEMPDIR`
