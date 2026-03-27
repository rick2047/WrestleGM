# Architecture and Design Patterns

This document provides a high-level overview of the application's architecture and the key design patterns used in its construction. Understanding these patterns is useful for a Product Owner as they explain how the application is built to be robust, maintainable, and extensible.

## High-Level Architecture

The application is built around a core **domain model** and a **deterministic simulation engine**. The user interface is a separate layer that interacts with this core.

```mermaid
graph TD
    subgraph UI Layer
        A[Textual UI <br>(Screens & Widgets)]
    end
    subgraph Core Logic Layer
        B[GameState]
        C[Simulation Engine]
        D[Data Models]
    end
    subgraph Data Layer
        E[JSON Files <br>(Wrestlers, Match Types)]
        F[Save Files <br>(Game State)]
    end

    A -- Reads from / Writes to --> B;
    B -- Uses --> C;
    B -- Contains --> D;
    C -- Uses --> D;
    B -- Loads from --> E;
    B -- Saves to / Loads from --> F;
```

-   **UI Layer:** Responsible for presenting the game to the user and capturing their input. It is built with the Textual framework.
-   **Core Logic Layer:** Contains the game's rules, state, and simulation logic. This is the "brains" of the application.
-   **Data Layer:** Responsible for loading initial game data (from JSON files) and persisting the game state (to save files).

This separation of concerns is crucial. It means we can change the UI without affecting the game's rules, and we can tweak the simulation without having to change the UI.

## Key Design Patterns

Design patterns are reusable solutions to common software design problems. Using them helps to make the application more flexible, understandable, and robust.

### State Management Pattern

-   **What it is:** A centralized model for managing the application's state.
-   **How we use it:** The `GameState` class is the single source of truth for the entire application. It holds all the current information about the game: the roster, the player's money, the current show card, etc.
-   **Why it's good for the product:**
    -   **Consistency:** By having a single place for all game data, we avoid inconsistencies and bugs.
    -   **Simplicity:** The UI layer becomes simpler. It just needs to read from the `GameState` to display information and call methods on `GameState` to perform actions.
    -   **Testability:** We can easily test the game logic by creating a `GameState` object and performing actions on it, without needing to interact with the UI.

### Strategy Pattern

-   **What it is:** A pattern that allows you to define a family of algorithms, put each of them into a separate class, and make their objects interchangeable.
-   **How we use it:** The `RatingModifier` system in the simulation engine is a perfect example of the Strategy pattern. Each modifier (e.g., `AlignmentModifier`, `RivalryModifier`) is its own "strategy" for adjusting a match's rating. The simulation engine can be configured with a list of these strategies.
-   **Why it's good for the product:**
    -   **Flexibility:** It's incredibly easy to add new rating modifiers or change existing ones without touching the core simulation logic.
    -   **Extensibility:** If we want to introduce a new gameplay mechanic that affects match ratings (e.g., a "Championship Bonus"), we can simply create a new `RatingModifier` class. This makes it easy to add new features.

### Service/Manager Pattern

-   **What it is:** A pattern where a class (a "manager" or "service") is responsible for a specific area of functionality.
-   **How we use it:** We have several manager classes:
    -   `SessionManager`: Manages the starting, saving, and loading of game sessions.
    -   `RivalryManager`: Manages the state of all rivalries between wrestlers.
    -   `EconomySimulator`: Manages the financial calculations for a show.
-   **Why it's good for the product:**
    -   **Organization:** It helps to organize the code by grouping related functionality together. This makes the code easier to understand and maintain.
    -   **Modularity:** Each manager is responsible for its own domain, which reduces complexity.

### Data Mapper / Repository Pattern

-   **What it is:** A pattern that separates the in-memory objects from the database (or in our case, data files).
-   **How we use it:** The functions in `wrestlegm/data.py` (e.g., `load_wrestlers`, `load_match_types`) act as a simple data mapper. They are responsible for reading the raw data from JSON files and mapping it into the application's data models (e.g., `WrestlerDefinition`).
-   **Why it's good for the product:**
    -   **Decoupling:** The core application doesn't need to know how or where the data is stored. We could change from JSON files to a database without having to change the game logic.
    -   **Maintainability:** All data loading logic is in one place, making it easy to manage.
