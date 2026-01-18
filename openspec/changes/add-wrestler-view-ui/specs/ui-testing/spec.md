## MODIFIED Requirements
### Requirement: UI snapshot tests
The system SHALL generate deterministic SVG snapshots for canonical UI screens and stable end states only using `pytest-textual-snapshot`.

#### Scenario: Canonical snapshot registry
- **WHEN** snapshot tests run
- **THEN** the snapshot registry is fixed to the following list:
  - S1 Main Menu (default)
  - S2 Game Hub (default)
  - S3 Booking Hub (all slots empty)
  - S4 Booking Hub (all slots filled)
  - S5 Wrestler View (empty)
  - S6 Wrestler View (filled)
  - S7 Match Booking (2-wrestler)
  - S8 Match Booking (multi-wrestler)
  - S9 Promo Booking (empty)
  - S10 Promo Booking (filled)
  - S11 Wrestler Selection (default)
  - S12 Wrestler Selection (inspection modal open)
  - S13 Match Booking Confirmation (modal visible)
  - S14 Show Results (default)
  - S15 Roster Overview (default)
