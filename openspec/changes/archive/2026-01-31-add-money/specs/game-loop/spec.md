## ADDED Requirements

### Requirement: Money updates after show resolution
The system SHALL update promotion money after a show completes and results are stored.

#### Scenario: Money updated after results
- **WHEN** a show finishes simulation and results are stored
- **THEN** money is updated using the computed show cost, gate income, and merch income

### Requirement: Bankruptcy gating before next show
The system SHALL check bankruptcy when the player attempts to book the next show and block play if no valid show can be afforded.

#### Scenario: Bankruptcy check timing
- **WHEN** the player leaves results and attempts to book the next show
- **THEN** the system evaluates whether any valid show can be afforded

#### Scenario: Bankruptcy triggers game over
- **WHEN** no valid 3-match, 2-promo card can be afforded with current money
- **THEN** the system transitions to Game Over: Bankruptcy
