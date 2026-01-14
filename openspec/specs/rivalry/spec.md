# rivalry Specification

## Purpose
TBD - created by archiving change add-rivalry-mechanic. Update Purpose after archive.
## Requirements
### Requirement: Pairwise rivalry and cooldown state tracking
The system SHALL track rivalry and cooldown state per unique wrestler pair using a normalized pair key and ensure that a pair can be in at most one state at a time: none, active rivalry, or cooldown.

#### Scenario: Normalized pair identity
- **WHEN** rivalry state is stored for wrestler A and wrestler B
- **THEN** the system uses a normalized pair key so A–B and B–A resolve to the same rivalry state

### Requirement: Rivalry progression from matches
The system SHALL create or advance an active rivalry for each wrestler pair that appears in the same match and is not in cooldown, and SHALL apply the progression at show end.

#### Scenario: Increment rivalry on match participation
- **WHEN** a match includes a pair that is not in cooldown
- **THEN** that pair's rivalry value increases by 1 at show end
- **AND THEN** the rivalry level is `min(4, rivalry_value)`

### Requirement: Blowoff resolution and cooldown start
The system SHALL treat matches involving a Level 4 rivalry pair as blowoff matches and, at show end, remove the rivalry state and create a cooldown state with six remaining shows.

#### Scenario: Blowoff creates cooldown
- **WHEN** a match includes a pair at rivalry level 4
- **THEN** the rivalry resolves at show end and a cooldown state is created with `remaining_shows = 6`

### Requirement: Cooldown behavior and timing
The system SHALL block rivalry progression and rivalry bonuses for pairs in cooldown, decrement cooldown at each show transition, and remove cooldown when it reaches zero.

#### Scenario: Cooldown blocks progression
- **WHEN** a pair is in cooldown and appears in a match
- **THEN** no rivalry progression occurs for that pair
- **AND THEN** the cooldown remaining shows still decrements at show end

### Requirement: Pairwise evaluation in multi-wrestler matches
The system SHALL evaluate rivalry and cooldown state for all unique wrestler pairs in a match.

#### Scenario: Multi-wrestler pair evaluation
- **WHEN** a match includes N wrestlers
- **THEN** rivalry and cooldown logic evaluates all `N·(N-1)/2` unique pairs

