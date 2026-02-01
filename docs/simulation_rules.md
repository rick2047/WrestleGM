# Simulation Rules

The simulation engine is the heart of WrestleGM, determining the outcomes and ratings of all in-ring action. This document breaks down the rules that govern the simulation, from a Product Owner's perspective. The goal is a system that is both believable and fun, rewarding smart booking decisions.

## Guiding Principles

-   **Popularity is King:** More popular wrestlers are more likely to win and have higher-rated matches.
-   **Booking Matters:** The choices the player makes when booking a match directly impact its quality.
-   **Storytelling Pays Off:** Building and concluding rivalries leads to the highest rewards.
-   **Everything has a Cost:** Every match has a physical toll, and every show has a financial one.

## Match Outcomes: Who Wins?

The winner of a match is determined by a weighted probability. The primary factor is **Popularity**, but a wrestler's **Stamina** also plays a role.

-   `Winner Likelihood = (Popularity * 70%) + (Stamina * 30%)`

Essentially, a wrestler's "power level" is a combination of their star power and their physical condition.

However, to keep things interesting, an **Outcome Chaos** factor is introduced by the chosen match type. This can be thought of as the "upset potential":

-   **Low Chaos (e.g., "Normal" match):** The more popular wrestler is very likely to win.
-   **High Chaos (e.g., "Battle Royal"):** Upsets are much more common, and the winner is less predictable.

## Match Ratings: Was it a Good Match?

The star rating of a match (0-5 stars) is a measure of its quality. It is calculated starting with a **Base Rating** and then adjusted by a series of modifiers.

### Base Rating

The base rating is determined by the average skill of the wrestlers involved.

-   `Base Rating = (Average Popularity * 60%) + (Average Stamina * 40%)`

A match between two highly popular, high-stamina wrestlers will have a high base rating.

### Rating Modifiers

This is where the player's booking decisions have the biggest impact. Modifiers can add or subtract from the base rating.

| Modifier | Description | Impact |
| :--- | :--- | :--- |
| **Alignment Bonus** | A classic "Good vs. Evil" (Face vs. Heel) matchup gets a bonus. | **++** |
| **Rivalry Bonus** | Wrestlers who are in an active rivalry get a significant bonus. | **+++** |
| **Rivalry Blow-off** | The final match of a rivalry (the "blow-off") gets the largest bonus. | **+++++** |
| **Match Type Bonus** | Certain exciting match types (e.g., "Ladder Match") provide a small inherent bonus. | **+** |
| **Heel vs. Heel** | Two "bad guys" fighting is generally less compelling and gets a penalty. | **--** |
| **Cooldown Penalty** | Booking wrestlers in a big match too soon after their rivalry has ended results in a significant penalty. This encourages a "cooldown" period. | **-----** |
| **Random Variance** | Every match type has a random variance factor. A match can be slightly better or worse than expected, just because. | **+/-** |

## Promo Ratings

Promos are rated based on a wrestler's **Mic Skill** and **Popularity**.

-   `Promo Rating = (Mic Skill * 70%) + (Popularity * 30%)`

A good promo increases a wrestler's popularity, while a poor one can decrease it.

## Stat Changes (Deltas)

After a match, wrestlers' stats change:

-   **Popularity:** Winners gain popularity, losers lose a smaller amount. The amount is determined by the match type.
-   **Stamina:** All participants lose stamina. The amount is determined by the match type, with winners often losing a bit less than losers. Wrestlers who are not booked on a show recover a fixed amount of stamina.

## Show Rating & Economy

-   **Show Rating:** The overall show rating is the average of all match and promo ratings on the card.
-   **Income:** The money earned from a show is based on the show's rating, the popularity of the wrestlers on the card, and the rivalries featured.
-   **Costs:** The cost of a show is the sum of the booking fees for all wrestlers on the card, plus any additional costs for special match types.
