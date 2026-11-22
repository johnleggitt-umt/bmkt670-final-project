# Dashboard Notes

## Who uses it?
This dashboard is designed for managers at video game studios making decisions about how much to continue to invest in a video game after it's been out for a year.

## What decision does it help with?
* Post-launch investment (updates, server planning, support)
* Paid add-ons, expansions, and downloadable content
* Sequels, ports, and remakes/remasters

## Structure
| Page |	Question it answers |
| --- | --- |
| 1. What happened | How do player counts change over the first three years of a game's release? How well does year 1 predict year 3? |
| 2. How good are the predictions |	Can we trust the model, and where does it miss? |
| 3. What should we do |	How should a studio plan post-launch support, and what is a game's likely year-three audience? |

## AI Feature
Page 3 contains AI summaries of the models predictions. Anthropic's model Haiku 5.5 was used for these summaries for 180 games in the test data set.

It was given the following prompt:
"You are writing for a game studio manager. In 2-3 plain sentences, summarize this player prediction. Use only the facts below and do not add information. Respond with only the summary."

And the following variables per API call:
game_name, release_year, initial_cost, month1_avg_players, month12_avg_players, m1_to_m12_retention, predicted, actual, miss (calculated as predicted minus actual)

### AI Summary Double Checks

Three games were selected to double check the results. In all three cases, the summary was completely correct.

1. **Assassin's Creed Valhalla**: The prediction for Assassin's Creed Valhalla (2022, $59.99) estimated 4,255 average players at month 36, but the actual figure was 7,314, a miss of 3,060 players. Month 1 averaged 5,156 players, and month 12 averaged 3,710, or 72% of month 1.

2. **FINAL FANTASY VII REMAKE INTERGRADE**: The model predicted that Final Fantasy VII Remake Intergrade (released 2022, priced at $39.99) would average 659 players at month 36, but it actually averaged 980, a miss of 321 players. The game started at 3,367 average players in month 1 and fell to 741 by month 12, or 22% of its launch level.

3. **The Last of Us™ Part I**: The Last of Us Part I, released in 2023 at $59.99, averaged 4,858 players in its first month and 1,086 by month 12, which was 22% of its month-1 level. The prediction for month 36 was 1,164 average players, but the actual figure was 1,877, a miss of 713 players.

### AI Costs
Claude Haiku 5.5 was given a max of 500 tokens for each API call, which translates to a cost of $0.00025 per API call. With 180 games in the data, the maximum possible cost to run the program is $0.045 (although in practice, it only cost about 2 cents).

## What else to add if more time?
1. **More months as features for the model**: Only using the twelve-month mark made it so the primary signal for the model was based on just one month. Battlefield V is the clearest case: a spike at year one caused the model to miss its target by a very large margin.
2. **Predict log player counts, not raw player counts**: The games in the data range from a few hundred players at launch to over a hundred thousand players at launch. Because the model is trained and scored on raw players, big games produce big misses even when the prediction is close in percentage terms.