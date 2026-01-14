## MODIFIED Requirements
### Requirement: Match booking flow
The system SHALL edit matches in a dedicated booking screen, require confirmation before committing, and split match category selection (size) from stipulation selection (rules). The booking screen SHALL open after a category is chosen, render one wrestler row per required slot based on category, filter stipulations to those allowed for the selected category, allow changing stipulation via an inline dropdown, default the stipulation to the first available option when booking an empty slot, mark already-booked wrestlers with a 📅 indicator in the selection list, show popularity and stamina, display alignment via emoji (Face 😃, Heel 😈), render the selection list as a table with Name/Stamina/Popularity columns, include a header row naming the name/stamina/popularity columns, format rows as `{emoji} {name:<18} {sta:>3} {pop:>3}{fatigue}{booked_marker}`, and use 🥱 consistently for low-stamina indicators.

#### Scenario: Stipulation dropdown opens on Enter
- **WHEN** the user focuses the stipulation dropdown in match booking
- **AND WHEN** they press Enter
- **THEN** the stipulation dropdown opens without error
