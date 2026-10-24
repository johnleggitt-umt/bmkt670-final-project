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
dim_user_tags = pd.DataFrame(tags).rename(columns={0: "tag_name"})
dim_user_tags = dim_user_tags.sort_values("tag_name").reset_index(drop=True)
dim_user_tags["user_tag_id"] = range(1, len(dim_user_tags) + 1)

# Printing results
print("dim_user_tags:")
dim_user_tags = dim_user_tags[["user_tag_id", "tag_name"]]
print(f"{len(dim_user_tags)} rows in dim_user_tags.")
dim_user_tags.to_csv("data/clean/dim_user_tags.csv", index=False)
print("dim_user_tags saved as data/clean/dim_user_tags.csv:")
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
fact_user_tag = fact_user_tag.merge(dim_user_tags, on="tag_name", how="left").drop(columns=["tag_name"])

# Printing results
print("fact_user_tag:")
fact_user_tag = fact_user_tag[["app_id", "user_tag_id", "user_tag_votes"]]
print(f"Dropped {len(fact_user_tag[fact_user_tag["user_tag_votes"].isna()])} rows of {len(fact_user_tag)} total rows from fact_user_tag due to receiving zero votes.")
fact_user_tag = fact_user_tag.dropna(subset="user_tag_votes")
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
fact_monthly_players = fact_monthly_players[["app_id", "month_id", "months_released", "avg_players", "peak_players"]]
print(f"Dropped {len(fact_monthly_players[fact_monthly_players["months_released"].isna()])} rows of {len(fact_monthly_players)} total rows from fact_monthly_players due to missing release dates.")
fact_monthly_players = fact_monthly_players.dropna(subset="months_released")
print(f"{len(fact_monthly_players)} remianing rows in fact_monthly_players.")
fact_monthly_players.to_csv("data/clean/fact_monthly_players.csv", index=False)
print("fact_user_tag saved as data/clean/fact_monthly_players.csv:")
print("")