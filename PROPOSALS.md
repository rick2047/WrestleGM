Here are three proposals to make the WrestleGM simulation system more modular, simpler to reason about, and easier to extend:

### 1. Decompose the `SimulationEngine` into Focused Simulators

**Problem:** The current `SimulationEngine` is a monolithic class that handles all aspects of simulation (outcomes, ratings, stat deltas, promos). This makes the class large, difficult to test in isolation, and harder to maintain as new simulation features are added.

**Proposal:** Break down the `SimulationEngine` into smaller, more focused classes, each responsible for a single aspect of the simulation. The main `SimulationEngine` would then become a coordinator that delegates to these specialized simulators.

**Example Structure:**

*   **`OutcomeSimulator`**: Responsible for determining the winner and losers of a match.
*   **`RatingSimulator`**: Responsible for calculating the star rating of a match.
*   **`StatDeltaSimulator`**: Responsible for calculating the changes in wrestler stats after a match.
*   **`PromoSimulator`**: Responsible for simulating promos.

**Benefits:**

*   **Improved Modularity:** Each class has a single, well-defined responsibility.
*   **Easier Testing:** Each simulator can be tested independently.
*   **Simplified Reasoning:** It's easier to understand the logic of a small, focused class than a large, multi-purpose one.
*   **Extensibility:** New simulation components can be added as new classes without modifying existing ones.

### 2. Introduce a "Modifier" System for Ratings

**Problem:** The `simulate_rating` function contains complex, hardcoded logic for applying rating adjustments, such as alignment bonuses. This makes it difficult to add new factors that might influence a match's rating.

**Proposal:** Implement a "modifier" system where a collection of modifier objects or functions can be applied to a base rating. Each modifier would encapsulate a single piece of rating logic.

**Example Modifiers:**

*   **`AlignmentModifier`**: Calculates a bonus or penalty based on the face/heel alignment of the wrestlers.
*   **`RivalryModifier`**: Applies a bonus if the match is part of an active rivalry.
*   **`TagTeamModifier`**: Applies a bonus if the wrestlers are part of an established tag team.
*   **`StyleClashModifier`**: Applies a bonus or penalty based on how well the wrestlers' styles mesh.

The `RatingSimulator` would iterate over a list of registered modifiers, applying each one to the match rating.

**Benefits:**

*   **Extensibility:** New rating factors can be added by creating new modifier classes, without changing the core rating simulation logic.
*   **Configurability:** Modifiers can be enabled, disabled, or configured on a per-match or global basis.
*   **Clarity:** The logic for each rating adjustment is isolated and easy to understand.

### 3. Model the Simulation as a Configurable Pipeline

**Problem:** The sequence of simulation steps for a match is hardcoded within the `simulate_match` method. This creates a rigid structure that is difficult to change or extend.

**Proposal:** Model the simulation process as a configurable pipeline of steps. Each step in the pipeline would be a function or object that takes the current simulation state and returns an updated state.

**Example Pipeline for a Match:**

1.  **`InitializeContext`**: Gathers all necessary data (wrestlers, match type, etc.).
2.  **`SimulateOutcome`**: Determines the winner and losers.
3.  **`SimulateRating`**: Calculates the initial star rating.
4.  **`ApplyRatingModifiers`**: Applies all registered rating modifiers.
5.  **`CalculateStatDeltas`**: Calculates the stat changes for each wrestler.
6.  **`FinalizeResult`**: Constructs the final `MatchResult` object.

The `SimulationEngine` would be responsible for executing the pipeline in the configured order.

**Benefits:**

*   **Flexibility:** The simulation process can be easily reconfigured by adding, removing, or reordering steps in the pipeline.
*   **Extensibility:** New simulation features (e.g., injuries, post-match events) can be added as new steps in the pipeline without modifying existing logic.
*   **Clarity:** The entire simulation process is explicitly defined by the pipeline configuration, making it easy to see how a final result is produced.
