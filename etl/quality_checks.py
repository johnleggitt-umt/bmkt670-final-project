import os
import psycopg2
from dotenv import load_dotenv
from pathlib import Path
import warnings
import pandas as pd

load_dotenv()

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DB_CONFIG = {
    "host": os.getenv("PGHOST"),
    "port": os.getenv("PGPORT"),
    "dbname": os.getenv("PGDATABASE"),
    "user": os.getenv("PGUSER"),
    "password": os.getenv("PGPASSWORD"),
}

warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# Dupes in ml_features_player_retention
cur.execute("""
    SELECT COUNT(*) - COUNT(DISTINCT app_id)
    FROM ml_features_player_retention;
""")
dupes1 = cur.fetchone()[0]

if dupes1 == 0:
    status = "PASS"
else:
    status = "FAIL"

print(f"[{status}] Check 1: Duplicate app_ids in ml_features_player_retention: {dupes1}")


# Dupes of month per game in fact_monthly_players
cur.execute("""
    SELECT COUNT(*) - COUNT(DISTINCT (app_id, month_id))
    FROM fact_monthly_players;
""")
dupes2 = cur.fetchone()[0]

if dupes2 == 0:
    status = "PASS"
else:
    status = "FAIL"

print(f"[{status}] Check 2: Duplicate game months in fact_monthly_players: {dupes2}")

# Negative player counts
cur.execute("""
    SELECT COUNT(*) 
    FROM fact_monthly_players WHERE avg_players < 0 OR peak_players < 0;
""")
negs = cur.fetchone()[0]

if negs == 0:
    status = "PASS"
else:
    status = "FAIL"

print(f"[{status}] Check 3: Negative players in fact_monthly_players: {negs}")

# Orphaned rows in fact_monthly_players
cur.execute("""
    SELECT COUNT(*) 
    FROM fact_monthly_players
    LEFT JOIN dim_game ON fact_monthly_players.app_id = dim_game.app_id
    WHERE dim_game.app_id IS NULL;
""")
orphans = cur.fetchone()[0]

if orphans == 0:
    status = "PASS"
else:
    status = "FAIL"

print(f"[{status}] Check 4: Orphaned rows in fact_monthly_players: {orphans}")

# dim_game matches raw minus unsuccessful downloads and null release dates

cur.execute("""
    SELECT COUNT(*) 
    FROM dim_game
""")
dim_game_rows = cur.fetchone()[0]

df_steamworks = pd.read_json("data/raw/steamworks_raw.json")
df_steamworks["success"] = df_steamworks["response"].str.get("success")
df_steamworks = df_steamworks[df_steamworks["success"] == True]
df_steamworks["data"] = df_steamworks["response"].str.get("data")
df_steamworks["release_date"] = df_steamworks["data"].str.get("release_date").str.get("date")
df_steamworks["release_date"] = pd.to_datetime(df_steamworks["release_date"], format="%b %d, %Y")
df_steamworks = df_steamworks.dropna(subset=["release_date"])

raw_rows = len(df_steamworks)


if dim_game_rows == raw_rows:
    status = "PASS"
else:
    status = "FAIL"

print(f"[{status}] Check 5: {dim_game_rows} rows in dim_game and {raw_rows} successful SteamWorks downloads with release dates")

# ml_features_player_retention split matches clean data

cur.execute("""
    SELECT COUNT(*) 
    FROM ml_features_player_retention
    WHERE split = 'train';
""")
train_count_sql = cur.fetchone()[0]

df_ml_features_player_retention = pd.read_csv("data/clean/ml_features_player_retention.csv")
train_count_source = df_ml_features_player_retention["split"].value_counts()["train"]

if train_count_sql == train_count_source:
    status = "PASS"
else:
    status = "FAIL"

print(f"[{status}] Check 6: {train_count_sql} training rows in ml_features_player_retention and {train_count_source} train in clean data")


conn.close()
