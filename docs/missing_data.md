| Table | Column | % missing | Decision | Why |
|---|---|---|---|---|
| df_steamworks | success | 1/2000 (in my download) | Drop | only one game won't make a difference. If many games are unsuccessfully downloaded it's worth running the extract programs again. |
| df_steamcharts | Month (where = "Last 30 Days") | 1837/206430 | Drop | Data is incomplete for last months and not needed to build the model anyway |
| dim_game | release_date | 17/1999 | Drop | If the release date is unpublished, we won't be able to run this analysis on it |
| fact_user_tag | user_votes | 809757/848000  | Drop | These are rows where the user tag does not apply to the game |
| fact_monthly_players | months_released | 1889/204593 | Drop | Dropped games from this where the column could not be calulated due to missing release_date in dim_game |