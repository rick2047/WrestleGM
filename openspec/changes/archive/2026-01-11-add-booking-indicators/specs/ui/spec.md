## MODIFIED Requirements
### Requirement: Match booking flow
The system SHALL edit matches in a dedicated booking screen and require confirmation before committing. The booking screen SHALL default the match type to the first match type entry, mark already-booked wrestlers with a 📅 indicator in the selection list, and use 🥱 consistently for low-stamina indicators.

#### Scenario: Confirmation modal on booking
- **WHEN** a booking is complete and the user selects Confirm
- **THEN** a modal prompts for final confirmation before saving the slot

#### Scenario: Default match type on booking
- **WHEN** the user opens match booking for an empty slot
- **THEN** the first available match type is pre-selected

#### Scenario: Booked wrestler indicator
- **WHEN** the user opens the wrestler selection list
- **THEN** already-booked wrestlers include a 📅 indicator in their row
- **AND THEN** wrestlers selected in the current booking draft also show the 📅 indicator

#### Scenario: Low-stamina indicator consistency
- **WHEN** the UI renders a low-stamina indicator
- **THEN** it uses the 🥱 emoji everywhere
