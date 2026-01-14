## ADDED Requirements
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
