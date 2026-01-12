## MODIFIED Requirements
### Requirement: Show validation rules
The system SHALL prevent running a show unless it has exactly three valid matches, two promos each with a wrestler assigned, no duplicate wrestlers across any slot, all match-booked wrestlers meet stamina requirements, each match includes exactly the number of wrestlers required by its selected match category, and each match type is allowed for its selected category.

#### Scenario: Block invalid show run
- **WHEN** the card is incomplete, contains duplicate wrestlers, has a match wrestler below stamina requirements, a match does not meet its required category size, or a match type is incompatible with its category
- **THEN** the system blocks simulation
