from bs4 import BeautifulSoup
import requests
import pandas as pd
import time


df_source = pd.read_json("data/raw/steamspy_raw.json")
df_source = df_source.T
app_ids = df_source["appid"]


games = []
skipped = []

for id in app_ids:
    time.sleep(1.5)
    r = requests.get(f"https://steamcharts.com/app/{id}", timeout=30)
    if r.status_code != 200:
        skipped.append((id, r.status_code))
        continue
        
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table")
    if table is None:
        skipped.append((id, "no table"))
        continue

    rows = []
    for tr in table.find_all("tr"):
        cells = [c.get_text(strip=True) for c in tr.find_all(["th", "td"])]
        rows.append(cells)
    game_df = pd.DataFrame(rows[1:], columns=rows[0])
    game_df["app_id"] = id
    games.append(game_df)
    

df = pd.concat(games)
df.to_csv("data/raw/steamcharts_raw.csv", index=False)

print(f"Downloaded {len(df)} rows")
