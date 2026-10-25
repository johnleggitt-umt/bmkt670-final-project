import os
from pathlib import Path
import warnings
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
from dotenv import load_dotenv

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

cur.execute("TRUNCATE dim_game, dim_user_tag, dim_month, fact_user_tag, fact_monthly_players, ml_features_player_retention CASCADE")

table_names = ['dim_game', 'dim_user_tag', 'dim_month', 'fact_user_tag', 'fact_monthly_players', 'ml_features_player_retention']
for table_name in table_names:
    df = pd.read_csv(f"data/clean/{table_name}.csv")
    execute_values(cur, f"INSERT INTO {table_name} VALUES %s", df.values.tolist())

conn.commit()
conn.close()


