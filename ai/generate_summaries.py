import os
from pathlib import Path
import warnings
import psycopg2
import pandas as pd
import anthropic
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Setting up environment
load_dotenv(Path(__file__).resolve().parent.parent / ".env")
client = anthropic.Anthropic()

warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")

DB_CONFIG = {
    "host": os.getenv("PGHOST"),
    "port": os.getenv("PGPORT"),
    "dbname": os.getenv("PGDATABASE"),
    "user": os.getenv("PGUSER"),
    "password": os.getenv("PGPASSWORD"),
}

conn = psycopg2.connect(**DB_CONFIG)

# Querying and processing data
query = """
SELECT p.app_id, g.game_name, m.release_year, m.initial_cost,
       m.month1_avg_players, m.month12_avg_players, m.m1_to_m12_retention,
       p.predicted, p.actual
FROM predictions p
JOIN dim_game g ON p.app_id = g.app_id
JOIN ml_features_player_retention m ON p.app_id = m.app_id
WHERE p.split = 'test'
"""

df = pd.read_sql(query, conn)
df["miss"] = df["actual"] - df["predicted"]

# Function for API calls
def summarize_game(game):
    response = client.messages.create(
        model="claude-haiku-5-5",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": (
                    "You are writing for a game studio manager. In 2-3 plain sentences, "
                    "summarize this player prediction. Use only the facts below and do not "
                    "add information. Respond with only the summary.\n\n"
                    f"Game: {game['game_name']}. "
                    f"Released: {game['release_year']}. "
                    f"Price: ${game['initial_cost']:.2f}. "
                    f"Average players in month 1: {game['month1_avg_players']:,.0f}. "
                    f"Average players at month 12: {game['month12_avg_players']:,.0f} "
                    f"({game['m1_to_m12_retention'] * 100:.0f}% of month 1). "
                    f"Predicted average players at month 36: {game['predicted']:,.0f}. "
                    f"Actual average players at month 36: {game['actual']:,.0f}. "
                    f"Miss: {game['miss']:,.0f} players."
                ),
            }
        ],
    )

    for block in response.content:
        if block.type == "text":
            return block.text

# Looping through games
games = df.to_dict(orient="records")
summaries = []
for game in games:
    summary = summarize_game(game)
    summaries.append(summary)

# Creating ai_summaries table in db
df["summary"] = summaries
df["created_at"] = pd.Timestamp.now()
df_summaries = df[["app_id", "summary", "created_at"]]

cur = conn.cursor()
cur.execute("TRUNCATE ai_summaries")
execute_values(cur, "INSERT INTO ai_summaries (app_id, summary, created_at) VALUES %s", df_summaries.values.tolist())
conn.commit()
conn.close()

print(f"Saved {len(df_summaries)} AI-generated summaries to the ai_summaries table")