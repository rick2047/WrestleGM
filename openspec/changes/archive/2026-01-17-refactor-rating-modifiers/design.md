# Design: Rating Modifier System

The core of this design is a new `RatingModifier` protocol (or abstract base class) that defines a standard interface for rating modifiers. The modifier interface accepts a match context object to keep the API extensible as new data needs emerge.

```python
from dataclasses import dataclass
from typing import List, Protocol
from wrestlegm.models import WrestlerState, MatchTypeDefinition

@dataclass(frozen=True)
class MatchContext:
    wrestlers: List[WrestlerState]
    match_type: MatchTypeDefinition
    rivalry_context: "RivalryRatingContext | None" = None

class RatingModifier(Protocol):
    """
    A protocol for classes that can modify a match rating based on
    the match context.
    """
    def calculate_modifier(
        self,
        context: MatchContext
    ) -> float:
        """
        Calculates a rating adjustment.

        Returns:
            A float to be added to the match rating (can be negative).
        """
        ...
```

The `SimulationEngine.simulate_rating` method will be refactored to accept a list of these `RatingModifier` objects. It will calculate a base rating and then iterate through the modifiers, summing their adjustments to produce the final rating.

## Modifier Implementations

### AlignmentModifier

This modifier will encapsulate the existing logic for face/heel alignment bonuses. It will be the first concrete implementation of the `RatingModifier` protocol.

### RivalryModifier

To demonstrate extensibility, a new `RivalryModifier` will be created. This will add a rating bonus to matches that are part of an active rivalry. This logic is currently handled outside the main rating simulation, but it fits naturally into the new modifier system.

## `SimulationEngine` Refactoring

The `simulate_rating` function will change from this:

```python
def simulate_rating(
    self,
    wrestlers: List[WrestlerState],
    match_type: MatchTypeDefinition,
) -> tuple[float, RatingDebug]:
    # ... complex alignment logic ...
```

To this:

```python
def simulate_rating(
    self,
    context: MatchContext,
    modifiers: List[RatingModifier],
) -> tuple[float, RatingDebug]:
    base_rating = # ... calculate base rating ...
    total_adjustment = sum(
        modifier.calculate_modifier(context) for modifier in modifiers
    )
    final_rating = base_rating + total_adjustment
    # ...
```

This approach decouples the core rating simulation from the specific business logic of rating adjustments, making the system more modular and extensible.
