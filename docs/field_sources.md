| Table | Field | Comes from | How | Used for |
|---|---|---|---|---|
|dim_game|app_id|SteamSpy|'appid' from the top 2000 list|Key|
|dim_game|game_name|SteamWorks|'name'|Dashboard|
|dim_game|developer|SteamWorks|'developers'|Dashboard, possible feature|
|dim_game|initial_cost|SteamWorks|'initialprice'|Dashboard, possible feature|
|dim_game|release_date|STeamSpy|'release_date'|feature|
|dim_game|store_category|SteamWorks|'categories'|input to features (one-hot encoding)|
|dim_user_tag|user_tag_id|Created in Python|Index|Key|
|dim_user_tag|tag_name|SteamSpy|'tags'|Dashboard|
|dim_month|month_id|SteamCharts|'Month'|Key|
|dim_month|year_num|Created in Python|Extract year from date|Dashboard|
|dim_month|month_num|Created in Python|Extract month from date|Dashboard|
|fact_user_tag|app_id|SteamWorks|'appid'|Key|
|fact_user_tag|user_tag_id|Created in Python|Index|Key|
|fact_user_tag|user_tag_votes|SteamSpy|'tags'|Feature|
|fact_monthly_players|app_id|SteamSpy|'appid'|Key|
|fact_monthly_players|month_id|SteamCharts|'Month'|Key|
|fact_monthly_players|avg_players|SteamCharts|'Avg. Players'|Feature|
|fact_monthly_players|peak_players|SteamCharts|'Peak Players'|Feature|
|fact_monthly_players|months_released|Created in Python|Subtract release date from month_id|Feature|