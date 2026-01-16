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

### Requirement: Card locking during simulation
The system SHALL lock the show card once simulation begins and prevent edits until results are available.

#### Scenario: Card locked while simulating
- **WHEN** a show enters simulation
- **THEN** the card cannot be edited until the show completes

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
The system SHALL use `STAMINA_MIN_BOOKABLE = 10` as the minimum stamina required to book a wrestler in a match.

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

### Requirement: Show lifecycle states
The system SHALL model show progression through Planning, Locked, Simulating, Completed, and Applied states.

#### Scenario: Show lifecycle progression
- **WHEN** a show is booked and run
- **THEN** it transitions through planning, locked, simulating, completed, and applied states

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
