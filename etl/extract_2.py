import pandas as pd
import requests
import json
import time

df = pd.read_json("data/raw/steamspy_raw.json")
df = df.T
app_ids = df["appid"].head(10)

games = []
for id in app_ids:
    r = requests.get("https://store.steampowered.com/api/appdetails",
                 params={"appids": id, "cc": "us"})
    data = r.json()[str(id)]
    games.append({"appid": id, "response": data})
    time.sleep(1.5)

with open("data/raw/steamworks_raw.json", "w") as f:
    json.dump(games, f)

print(f"Downloaded {len(games)} rows")