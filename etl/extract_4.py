import pandas as pd
import requests
import json
import time

df = pd.read_json("data/raw/steamspy_raw.json")
df = df.T
app_ids = df["appid"]

games = []
for id in app_ids:
    r = requests.get("https://steamspy.com/api.php",
                 params={"request": "appdetails", "appid": id})
    data = r.json()
    games.append({"appid": id, "response": data})
    time.sleep(1)

with open("data/raw/steamspy_tags_raw.json", "w") as f:
    json.dump(games, f)

print(f"Downloaded {len(games)} rows")