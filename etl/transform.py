import pandas as pd

df_steamspy = pd.read_json("data/raw/steamspy_raw.json")
df_steamspy = df_steamspy.T
df_steamworks = pd.read_json("data/raw/steamworks_raw.json")
df_steamspy_tags = pd.read_json("data/raw/steamspy_tags_raw.json")
df_steamcharts = pd.read_csv("data/raw/steamcharts_raw.csv")

print("Initial Data Cleaning:")
# Checking for successful download in SteamWorks and dropping bad results
df_steamworks["success"] = df_steamworks["response"].str.get("success")

print(f"Dropped {len(df_steamworks[df_steamworks['success'] == False])} rows of {len(df_steamworks)} total rows from SteamWorks data due to unsuccessful API call.")
df_steamworks = df_steamworks[df_steamworks["success"] == True]

df_steamworks["data"] = df_steamworks["response"].str.get("data")
df_steamworks = df_steamworks.drop(columns=["response","success"])

# Filtering out recent incomplete data in SteamCharts download
print(f"Dropped {len(df_steamcharts[df_steamcharts['Month'] == 'Last 30 Days'])} rows of {len(df_steamcharts)} total rows from SteamCharts data due to being too recent (Last 30 Days).")
print("")
df_steamcharts = df_steamcharts[df_steamcharts["Month"] != "Last 30 Days"]



# Building dim_game table
dim_game = pd.DataFrame(df_steamspy["appid"])
dim_game = dim_game.rename(columns={"appid": "app_id"})
dim_game = dim_game.reset_index(drop=True)

df_steamworks["game_name"] = df_steamworks["data"].str.get("name")
dim_game = dim_game.merge(df_steamworks[["appid", "game_name"]], left_on="app_id", right_on="appid", how="left").drop(columns=["appid"])

df_steamspy["initial_cost"] = df_steamspy["initialprice"]
dim_game = dim_game.merge(df_steamspy[["appid", "initial_cost"]], left_on="app_id", right_on="appid", how="left").drop(columns=["appid"])
dim_game["initial_cost"] = pd.to_numeric(dim_game["initial_cost"])
dim_game["initial_cost"] = dim_game["initial_cost"]/100

df_steamworks["release_date"] = df_steamworks["data"].str.get("release_date").str.get("date")
dim_game = dim_game.merge(df_steamworks[["appid", "release_date"]], left_on="app_id", right_on="appid", how="left").drop(columns=["appid"])
dim_game["release_date"] = pd.to_datetime(dim_game["release_date"], format="%b %d, %Y")

'''
Keeping this code for now as a way to add one-hot encoding for categories if we explore this option later:
df_steamworks["categories"] = df_steamworks["data"].str.get("categories")
df_categories = df_steamworks[["appid", "categories"]].explode("categories")
df_categories["category"] = df_categories["categories"].str.get("description")
df_categories = df_categories.drop(columns=["categories"]).drop_duplicates()
df_categories = df_categories.pivot_table(index="appid", columns="category", aggfunc="size", fill_value=0) > 0
df_categories = df_categories.reset_index()
dim_game = dim_game.merge(df_categories, left_on="app_id", right_on="appid", how="left").drop(columns=["appid"])
'''

# Handling missing values and printing results
print("dim_game:")
dim_game = dim_game[["app_id", "game_name", "release_date", "initial_cost"]]
print(f"Dropped {len(dim_game[dim_game["game_name"].isna()])} rows of {len(dim_game)} total rows from dim_game due to unsuccessful SteamWorks API call.")
dim_game = dim_game.dropna(subset=["game_name"])
print(f"Dropped {len(dim_game[dim_game["release_date"].isna()])} rows of {len(dim_game)} remaining rows from dim_game due to missing release date.")
dim_game = dim_game.dropna(subset=["release_date"])
print(f"{len(dim_game)} remaining rows in dim_game.")


dim_game.to_csv("data/clean/dim_game.csv", index=False)
print("dim_game saved as data/clean/dim_game.csv:")
print("")

# Building dim_user_tag table
tags = []
for tag in df_steamspy_tags["response"].str.get("tags"):
    if isinstance(tag, dict):
        for tag_name in tag.keys():
            tags.append(tag_name)

tags = set(tags)
dim_user_tag = pd.DataFrame(tags).rename(columns={0: "tag_name"})
dim_user_tag = dim_user_tag.sort_values("tag_name").reset_index(drop=True)
dim_user_tag["user_tag_id"] = range(1, len(dim_user_tag) + 1)

# Printing results
print("dim_user_tag:")
dim_user_tag = dim_user_tag[["user_tag_id", "tag_name"]]
print(f"{len(dim_user_tag)} rows in dim_user_tag")
dim_user_tag.to_csv("data/clean/dim_user_tag.csv", index=False)
print("dim_user_tag saved as data/clean/dim_user_tag.csv:")
print("")

# Building dim_month table

df_steamcharts["date"] = pd.to_datetime(df_steamcharts["Month"], format="%B %Y")
months_set = set(df_steamcharts["date"])
dim_month = pd.DataFrame(months_set).rename(columns={0: "month_id"})
dim_month = dim_month.sort_values("month_id").reset_index(drop=True)
dim_month["year_num"] = dim_month["month_id"].dt.year
dim_month["month_num"] = dim_month["month_id"].dt.month

# Printing results
print("dim_month:")
dim_month = dim_month[["month_id", "year_num", "month_num"]]
print(f"{len(dim_month)} rows in dim_month.")
dim_month.to_csv("data/clean/dim_month.csv", index=False)
print("dim_month saved as data/clean/dim_month.csv:")
print("")

# Building fact_user_tag table

clean_tags = []
for tag in df_steamspy_tags["response"].str.get("tags"):
    if isinstance(tag, dict):
        clean_tags.append(tag)
    else:
        clean_tags.append({})

fact_user_tag = pd.json_normalize(clean_tags)
fact_user_tag["app_id"] = df_steamspy_tags["appid"]
fact_user_tag = fact_user_tag.melt(id_vars="app_id")
fact_user_tag = fact_user_tag.rename(columns={"variable": "tag_name","value": "user_tag_votes"})
fact_user_tag["user_tag_votes"] = fact_user_tag["user_tag_votes"]
fact_user_tag = fact_user_tag.merge(dim_user_tag, on="tag_name", how="left").drop(columns=["tag_name"])

# Printing results
print("fact_user_tag:")
fact_user_tag = fact_user_tag[["app_id", "user_tag_id", "user_tag_votes"]]
print(f"Dropped {len(fact_user_tag[fact_user_tag["user_tag_votes"].isna()])} rows of {len(fact_user_tag)} total rows from fact_user_tag due to receiving zero votes.")
fact_user_tag = fact_user_tag.dropna(subset="user_tag_votes")
in_dim_game = fact_user_tag["app_id"].isin(dim_game["app_id"])
print(f"Dropped {len(fact_user_tag) - in_dim_game.sum()} rows of {len(fact_user_tag)} remaining rows from fact_user_tag due to games not in dim_game.")
fact_user_tag = fact_user_tag[in_dim_game]
print(f"{len(fact_user_tag)} remianing rows in fact_user_tag.")
fact_user_tag.to_csv("data/clean/fact_user_tag.csv", index=False)
print("fact_user_tag saved as data/clean/fact_user_tag.csv:")
print("")


# Building fact_monthly_players table

fact_monthly_players = df_steamcharts.drop(columns=["Gain", "% Gain","Month"])
fact_monthly_players = fact_monthly_players.rename(columns={"Avg. Players": "avg_players", "Peak Players": "peak_players", "date": "month_id"})
fact_monthly_players = fact_monthly_players.merge(dim_game[["app_id", "release_date"]], on="app_id", how="left")

current_month = fact_monthly_players["month_id"]
release = fact_monthly_players["release_date"]

fact_monthly_players["months_released"] = (current_month.dt.year - release.dt.year) * 12 + (current_month.dt.month - release.dt.month)

fact_monthly_players = fact_monthly_players.drop(columns=["release_date"])

# Printing results
print("fact_monthly_players:")
fact_monthly_players = fact_monthly_players[["app_id", "month_id", "avg_players", "peak_players", "months_released"]]
print(f"Dropped {len(fact_monthly_players[fact_monthly_players["months_released"].isna()])} rows of {len(fact_monthly_players)} total rows from fact_monthly_players due to missing release dates in dim_game.")
fact_monthly_players = fact_monthly_players.dropna(subset="months_released")
print(f"{len(fact_monthly_players)} remianing rows in fact_monthly_players.")
fact_monthly_players.to_csv("data/clean/fact_monthly_players.csv", index=False)
print("fact_user_tag saved as data/clean/fact_monthly_players.csv:")
print("")


# ---------------------------------------------------------------------------
# AI-generated code: the section below was written by Claude (Anthropic)
# to build the ml_features_player_retention table. Reviewed and run by John.
# ---------------------------------------------------------------------------

# Building ml_features_player_retention table

# Average players at months 1, 12, and 36, one column each
key_months = fact_monthly_players[fact_monthly_players["months_released"].isin([1, 12, 36])]
avg_players = key_months.pivot_table(index="app_id", columns="months_released", values="avg_players")
avg_players = avg_players.rename(columns={1: "month1_avg_players", 12: "month12_avg_players", 36: "month36_avg_players"})
avg_players = avg_players.reset_index()

# Peak players in month 1
month1_peak = fact_monthly_players[fact_monthly_players["months_released"] == 1][["app_id", "peak_players"]]
month1_peak = month1_peak.rename(columns={"peak_players": "month1_peak_players"})

# Start from dim_game and join the player counts
ml_features = dim_game[["app_id", "release_date", "initial_cost"]].copy()
ml_features["release_year"] = ml_features["release_date"].dt.year
ml_features = ml_features.merge(avg_players, on="app_id")
ml_features = ml_features.merge(month1_peak, on="app_id")

# Keep games that have all three months (no month 36 = nothing to learn from)
ml_features = ml_features.dropna(subset=["month1_avg_players", "month12_avg_players", "month36_avg_players"])
ml_features = ml_features[ml_features["month1_avg_players"] > 0]   # can't divide by zero below

# Derived features
ml_features["m1_to_m12_retention"] = ml_features["month12_avg_players"] / ml_features["month1_avg_players"]
ml_features["m1_peak_m1_avg_ratio"] = ml_features["month1_peak_players"] / ml_features["month1_avg_players"]

# One-hot encoded top 10 user tags (1 = game has the tag, 0 = it doesn't)
top_tags = {
    "Singleplayer": "tag_singleplayer",
    "Action": "tag_action",
    "Multiplayer": "tag_multiplayer",
    "Adventure": "tag_adventure",
    "Atmospheric": "tag_atmospheric",
    "Co-op": "tag_co_op",
    "Open World": "tag_open_world",
    "Indie": "tag_indie",
    "RPG": "tag_rpg",
    "First-Person": "tag_first_person",
}
game_tags = fact_user_tag.merge(dim_user_tag, on="user_tag_id")
game_tags = game_tags[game_tags["tag_name"].isin(top_tags.keys())]
tag_onehot = pd.crosstab(game_tags["app_id"], game_tags["tag_name"]).rename(columns=top_tags).reset_index()

ml_features = ml_features.merge(tag_onehot, on="app_id", how="left")
tag_columns = list(top_tags.values())
ml_features[tag_columns] = ml_features[tag_columns].fillna(0).astype(int)

# Split by release year
ml_features["split"] = "train"
ml_features.loc[ml_features["release_year"].between(2020, 2021), "split"] = "validate"
ml_features.loc[ml_features["release_year"] >= 2022, "split"] = "test"

# Printing results
print("ml_features_player_retention:")
ml_features = ml_features[["app_id", "release_year", "initial_cost",
                           "month1_avg_players", "month1_peak_players", "month12_avg_players", "month36_avg_players",
                           "m1_to_m12_retention", "m1_peak_m1_avg_ratio"] + tag_columns + ["split"]]
print(f"{len(ml_features)} rows in ml_features_player_retention.")
print(ml_features["split"].value_counts())
ml_features.to_csv("data/clean/ml_features_player_retention.csv", index=False)
print("ml_features_player_retention saved as data/clean/ml_features_player_retention.csv")
print("")