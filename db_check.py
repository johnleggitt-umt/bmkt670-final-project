import os
from pathlib import Path
import warnings
import psycopg2
import pandas as pd
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

DB_CONFIG = {
    "host": os.getenv("PGHOST"),
    "port": os.getenv("PGPORT"),
    "dbname": os.getenv("PGDATABASE"),
    "user": os.getenv("PGUSER"),
    "password": os.getenv("PGPASSWORD"),
}

warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")

table_names = ['dim_game', 'dim_user_tag', 'dim_month', 'fact_user_tag', 'fact_monthly_players']
for table_name in table_names:
    QUERY = f"SELECT * FROM {table_name}"
    conn = psycopg2.connect(**DB_CONFIG)
    df = pd.read_sql(QUERY, conn)
    print(table_name)
    print(df)
    print("")
    conn.close()
  