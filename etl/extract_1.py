import json
import requests
import time

pages = [0, 1]

all_games = {}
for page in pages:
    r = requests.get("https://steamspy.com/api.php",
                     params={"request": "all", "page": page})
    all_games.update(r.json())
    if page != pages[-1]:
        time.sleep(60)

with open("data/raw/steamspy_raw.json", "w") as f:
    json.dump(all_games, f)

print(f"Downloaded {len(all_games)} rows")