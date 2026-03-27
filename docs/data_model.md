# Data Model

The data model is the backbone of WrestleGM, defining the structure of all the information in the game. This document explains the key data entities and their relationships in a way that is easy for a Product Owner to understand.

## Data Model Diagram

```mermaid
classDiagram
    direction LR

    class Wrestler {
        <<Entity>>
        id: str
        name: str
        alignment: "Face" or "Heel"
        popularity: int (0-100)
        stamina: int (0-100)
        mic_skill: int (0-100)
        description: str
        booking_price: int
    }

    class MatchType {
        <<Entity>>
        id: str
        name: str
        description: str
        base_cost: int
        modifiers: MatchTypeModifiers
    }

    class MatchTypeModifiers {
        <<Value Object>>
        outcome_chaos: float
        rating_bonus: int
        rating_variance: int
        stamina_cost_winner: int
        stamina_cost_loser: int
        popularity_delta_winner: int
        popularity_delta_loser: int
    }

    class Show {
        <<Entity>>
        show_index: int
        scheduled_slots: List[ShowSlot]
        results: List[ShowResult]
        show_rating: float
        audience: int
        gate_income: int
        merch_income: int
        total_earned: int
        show_cost: int
    }

    class ShowSlot {
        <<Value Object>>
        (A Match or a Promo)
    }

    class Match {
        <<Value Object>>
        wrestlers: List[Wrestler]
        match_type: MatchType
    }

    class Promo {
        <<Value Object>>
        wrestler: Wrestler
    }

    class Rivalry {
        <<Entity>>
        wrestler_a: Wrestler
        wrestler_b: Wrestler
        rivalry_value: int (0-100)
    }

    class Cooldown {
        <<Entity>>
        wrestler_a: Wrestler
        wrestler_b: Wrestler
        remaining_shows: int
    }

    Wrestler "many" -- "1" Match : (participates in)
    Wrestler "1" -- "1" Promo : (cuts)
    Wrestler "2" -- "1" Rivalry : (are in)
    Wrestler "2" -- "1" Cooldown : (are in)
    MatchType "1" -- "1" Match : (defines)
    MatchType "1" -- "1" MatchTypeModifiers : (has)
    Show "1" -- "many" ShowSlot : (contains)
    ShowSlot "1" -- "1" Match : (can be a)
    ShowSlot "1" -- "1" Promo : (can be a)
```

## Entity Descriptions

### Wrestler

This is the central entity in the game. A wrestler represents an individual performer in the player's promotion.

-   **Key Attributes:**
    -   `popularity`: How famous the wrestler is. This is a key driver for match ratings and winning probability.
    -   `stamina`: The wrestler's physical conditioning. It affects their ability to win matches and is depleted after each match.
    -   `mic_skill`: How good the wrestler is at talking. This is the primary factor for promo ratings.
    -   `alignment`: Whether the wrestler is a "Face" (good guy) or a "Heel" (bad guy). This affects match ratings.
    -   `booking_price`: The cost to book the wrestler for a show. This increases as their popularity grows.

### Match Type

This entity defines a specific type of wrestling match that can be booked.

-   **Key Attributes:**
    -   `base_cost`: The base cost to book this type of match.
    -   `modifiers`: A set of rules that affect the simulation of this match type (see `MatchTypeModifiers`).

### Match Type Modifiers

This is a "Value Object" that holds all the simulation modifiers for a `MatchType`. It's not an entity on its own, but rather a collection of attributes that belong to a `MatchType`. It includes things like `outcome_chaos`, `rating_bonus`, and stat change deltas.

### Show

A `Show` represents a single event that the player books. It contains the card, the results, and the financial outcome.

### Show Slot (Match / Promo)

A `Show` is made up of a list of `ShowSlot`s. A `ShowSlot` is simply a container that can hold either a `Match` or a `Promo`. This is how the show's card is built.

### Rivalry

A `Rivalry` represents a feud between two wrestlers.

-   **Key Attributes:**
    -   `rivalry_value`: A number from 0-100 that indicates the intensity of the rivalry. A higher value leads to a larger bonus in match ratings. This value increases when the wrestlers interact in matches and promos.

### Cooldown

A `Cooldown` is created after a rivalry ends. It's a temporary state between two wrestlers that prevents them from being booked together in a major match too soon. This encourages booking variety.

-   **Key Attributes:**
    -   `remaining_shows`: The number of shows for which the cooldown is active.
