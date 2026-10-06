from bs4 import BeautifulSoup
import requests
import pandas as pd
import time


df_source = pd.read_json("data/raw/steamspy_raw.json")
df_source = df_source.T
app_ids = df_source["appid"].head(10)


games = []
for id in app_ids:
    r = requests.get(f"https://steamcharts.com/app/{id}")
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table")
    rows = []
    for tr in table.find_all("tr"):
        cells = [c.get_text(strip=True) for c in tr.find_all(["th", "td"])]
        rows.append(cells)
    game_df = pd.DataFrame(rows[1:], columns=rows[0])
    game_df["app_id"] = id
    games.append(game_df)
    time.sleep(1.5)

df = pd.concat(games)
df.to_csv("data/raw/steamcharts_raw.csv", index=False)

print(f"Downloaded {len(df)} rows")
