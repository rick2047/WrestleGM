## ADDED Requirements
### Requirement: Save slot storage and file naming
The system SHALL store save data under `dist/data/save` using fixed filenames per slot: `slot_1.json`, `slot_2.json`, and `slot_3.json` for the MVP. The system SHALL treat slots as future-safe up to five slots without changing the file naming convention for the first three slots.

#### Scenario: Save file location and naming
- **WHEN** the system saves slot 2
- **THEN** it writes `dist/data/save/slot_2.json`

### Requirement: Save slot metadata and naming
Each save slot SHALL include `slot_index`, `name`, `exists`, and `last_saved_show_index` metadata. The slot name SHALL be immutable after the first save.

#### Scenario: First save requires naming
- **WHEN** a player saves into an unused slot
- **THEN** the system prompts for a non-empty slot name and stores it with the save metadata

#### Scenario: Slot name remains unchanged
- **WHEN** a player saves to an existing slot
- **THEN** the slot name is preserved and not changed

#### Scenario: Slot metadata is tracked
- **WHEN** the slot list is shown
- **THEN** each slot includes its index, name if present, exists flag, and last saved show index if present

### Requirement: Save payload and versioning
Save files SHALL be JSON, human-readable, and include a mandatory `version` field. MVP supports only `version = 1`; loading a higher version SHALL be blocked. Save payloads SHALL include the full game state required to resume planning the next show, including roster stats, current show index, current card state, and the RNG seed. If a `saved_at` field is present, it SHALL be metadata-only and MUST NOT influence simulation.

#### Scenario: Unsupported version blocks load
- **WHEN** a player attempts to load a save with `version` greater than 1
- **THEN** loading is blocked with an error

#### Scenario: Save includes RNG seed
- **WHEN** a save is created
- **THEN** the RNG seed is persisted alongside the other game state fields

### Requirement: Save timing and consistency
The system SHALL autosave when the player presses Continue on the Results screen after show application and recovery complete. Saves SHALL not occur during booking, simulation, or while viewing results. Autosave SHALL overwrite the currently loaded slot. Saves SHALL always represent a clean show boundary state.

#### Scenario: Autosave on results continue
- **WHEN** the player presses Continue on the Results screen
- **THEN** the current slot is saved before navigation away from the results

#### Scenario: No save during booking or simulation
- **WHEN** the show is being booked or simulated
- **THEN** no save is written

#### Scenario: No save while viewing results
- **WHEN** the Results screen is displayed before Continue
- **THEN** no save is written

### Requirement: Load behavior and landing screen
Loading a save SHALL restore the exact saved state and resume at a clean show boundary in the planning phase. Loading SHALL navigate directly to the Booking Hub and SHALL bypass new-game initialization.

#### Scenario: Load resumes planning on booking hub
- **WHEN** the player loads a save slot
- **THEN** the Booking Hub is shown with the restored show state

### Requirement: Save controls and non-rules
The system SHALL not provide manual save actions, mid-show saves, or save-on-quit behavior unless a show has completed and the player presses Continue. Save slots SHALL not be renamed or deleted in the MVP.

#### Scenario: No manual save actions
- **WHEN** the player navigates the UI
- **THEN** no manual save action is offered

#### Scenario: No save on quit without completion
- **WHEN** the player quits before completing a show
- **THEN** no save is written

### Requirement: Persistence ownership boundaries
Persistence orchestration SHALL be owned by `GameState`, which exposes save/load and new-game operations to the UI layer. Simulation and show application layers SHALL not perform file I/O, and `ShowApplier` SHALL not perform file I/O.

#### Scenario: No persistence in show applier
- **WHEN** show deltas are applied
- **THEN** no save or load file I/O occurs in the applier

#### Scenario: UI delegates persistence to game state
- **WHEN** the UI needs to save, load, or start a new game
- **THEN** it invokes `GameState` persistence operations rather than handling file I/O directly

### Requirement: RNG determinism across save/load
Save/load SHALL not introduce RNG draws and SHALL reuse the saved RNG seed verbatim.

#### Scenario: Deterministic outcome after load
- **WHEN** the player saves, exits, loads, and runs the next show with identical bookings
- **THEN** simulation results match the outcomes from a continuous session
