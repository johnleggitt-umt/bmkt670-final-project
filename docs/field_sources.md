| Table | Field | Comes from | How | Used for |
|---|---|---|---|---|
|dim_game|app_id|SteamSpy|'appid' from the top 2000 list|Key|
|dim_game|game_name|SteamWorks|'name'|Dashboard|
|dim_game|initial_cost|SteamSpy|'initialprice'|Dashboard, feature|
|dim_game|release_date|SteamSpy|'release_date'|feature|
|dim_user_tag|user_tag_id|Created in Python|Index|Key|
|dim_user_tag|tag_name|SteamSpy|'tags'|Dashboard|
|dim_month|month_id|SteamCharts|'Month'|Key|
|dim_month|year_num|Created in Python|Extract year from date|Dashboard|
|dim_month|month_num|Created in Python|Extract month from date|Dashboard|
|fact_user_tag|app_id|SteamSpy|'appid'|Key|
|fact_user_tag|user_tag_id|Created in Python|Index|Key|
|fact_user_tag|user_tag_votes|SteamSpy|'tags'|Feature|
|fact_monthly_players|app_id|SteamSpy|'appid'|Key|
|fact_monthly_players|month_id|SteamCharts|'Month'|Key|
|fact_monthly_players|avg_players|SteamCharts|'Avg. Players'|Feature|
|fact_monthly_players|peak_players|SteamCharts|'Peak Players'|Feature|
|fact_monthly_players|months_released|Created in Python|Subtract release date from month_id|Feature|
| ml_features_player_retention | app_id | dim_game | Merged | Key |
| ml_features_player_retention | release_year | dim_game | Merged | Feature + Splitting data <2020=Train, 2020/21=Validate, >2021=Test |
| ml_features_player_retention | initial_cost | dim_game | Merged | Feature |
| ml_features_player_retention | month1_avg_players | fact_monthly_players | Merged | Feature |
| ml_features_player_retention | month1_peak_players | fact_monthly_players | Merged | Feature |
| ml_features_player_retention | month12_avg_players | fact_monthly_players | Merged | Feature |
| ml_features_player_retention | month36_avg_players | fact_monthly_players | Merged | Target variable |
| ml_features_player_retention | m1_to_m12_retention | Created in Python | Divide m12 avg by m1 avg  | Feature |
| ml_features_player_retention | m1_peak_m1_avg_ratio | Created in Python | Divide m1 peak by m1 avg | Feature |
| ml_features_player_retention | tag_singleplayer | fact_user_tag | one-hot encoding | Feature |
| ml_features_player_retention | tag_action | fact_user_tag | one-hot encoding | Feature |
| ml_features_player_retention | tag_multiplayer | fact_user_tag | one-hot encoding | Feature |
| ml_features_player_retention | tag_adventure | fact_user_tag | one-hot encoding | Feature |
| ml_features_player_retention | tag_atmospheric | fact_user_tag | one-hot encoding | Feature |
| ml_features_player_retention | tag_co_op | fact_user_tag | one-hot encoding | Feature |
| ml_features_player_retention | tag_open_world | fact_user_tag | one-hot encoding | Feature |
| ml_features_player_retention | tag_indie | fact_user_tag | one-hot encoding | Feature |
| ml_features_player_retention | tag_rpg | fact_user_tag | one-hot encoding | Feature |
| ml_features_player_retention | tag_first_person | fact_user_tag | one-hot encoding | Feature |
| ml_features_player_retention | split | Created in Python | See above in release_date | Split |