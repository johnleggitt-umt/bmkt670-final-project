import os
from pathlib import Path
import warnings
import psycopg2
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
from sklearn.metrics import mean_absolute_error
import joblib


# Setting up environment
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")

DB_CONFIG = {
    "host": os.getenv("PGHOST"),
    "port": os.getenv("PGPORT"),
    "dbname": os.getenv("PGDATABASE"),
    "user": os.getenv("PGUSER"),
    "password": os.getenv("PGPASSWORD"),
}

conn = psycopg2.connect(**DB_CONFIG)

# Querying and processing data and loading model
query = """
SELECT predicted, actual
FROM predictions
WHERE split = 'test'
"""

df = pd.read_sql(query, conn)
test_mae = mean_absolute_error(df["actual"], df["predicted"])

model = joblib.load(Path(__file__).resolve().parent.parent / "model" / "player_model.joblib")

# Creating dashboard page
st.title("What Should We Do?")
st.caption("Actionable insights from the data.")

st.subheader("Recommendations")

# Recommendations
st.success("**1. Put the most support into launch, then scale down after six months.** Player counts level at around six months after launch (Page 1). " \
"The first few months are when servers and support are the most important.")

st.success("**2. Make the year-three call at month 12, not at launch.** Games that hold players at month 12 tend to hold them at month 36. (Page 1) " \
"The one-year mark is the right time to decide whether to invest (DLC, expansions, etc) or to wind down.")

st.success(f"**3. Plan around a range, not a single number.** The model's typical miss on new games is about {test_mae:,.0f} players (Page 2).")

st.warning("**Limit: The model only sees a game's own numbers.** It can't tell what caused a month-12 bump, so be wary of things like " \
"promotions near the end of year one that might give the model the wrong idea (Page 2).")

# Prediction tool
st.subheader("Predict a game's players at year three")
st.caption("This tool allows you to enter criteria about a game at the end of the first year and predict what the numbers might look like in year three")

c1, c2  = st.columns(2)
release_year = c1.number_input("Release year", min_value=2012, max_value=2030, value=2024)
price = c2.number_input("Launch price ($)", min_value=0.0, value=19.99)

c3, c4, c5 = st.columns(3)
m1_avg = c3.number_input("Month 1 avg. concurrent players", min_value=1, value=1000)
m1_peak = c4.number_input("Month 1 peak concurrent players", min_value=1, value=2500)
m12_avg = c5.number_input("Month 12 avg. concurrent players", min_value=0, value=300)

tag_labels = {
    "tag_singleplayer": "Single-player",
    "tag_action": "Action",
    "tag_multiplayer": "Multiplayer",
    "tag_adventure": "Adventure",
    "tag_atmospheric": "Atmospheric",
    "tag_co_op": "Co-op",
    "tag_open_world": "Open world",
    "tag_indie": "Indie",
    "tag_rpg": "RPG",
    "tag_first_person": "First person",
}

st.write("Tags")
features = {}
tag_cols = st.columns(5)
for i, tag in enumerate(tag_labels):
    with tag_cols[i % 5]:
        features[tag] = int(st.checkbox(tag_labels[tag]))

features["release_year"] = release_year
features["initial_cost"] = price
features["month1_avg_players"] = m1_avg
features["month1_peak_players"] = m1_peak
features["month12_avg_players"] = m12_avg
features["m1_to_m12_retention"] = m12_avg / m1_avg
features["m1_peak_m1_avg_ratio"] = m1_peak / m1_avg

X = pd.DataFrame([features])[model.feature_names_in_]

prediction = model.predict(X)[0]
low = max(0, prediction - test_mae)
high = prediction + test_mae

k1, k2 = st.columns(2)
k1.metric("Predicted month 36 avg. concurrent players", f"{prediction:,.0f}")
k2.metric("Likely range (± test MAE)", f"{low:,.0f} – {high:,.0f}")


# AI Summaries
s_query = """
    SELECT g.game_name, s.summary
    FROM ai_summaries s
    JOIN dim_game g ON s.app_id = g.app_id
    ORDER BY g.game_name
"""

summaries = pd.read_sql(s_query, conn)
conn.close()

st.subheader("AI summaries of test-game predictions")
game = st.selectbox("Game", summaries["game_name"])
st.write(summaries[summaries["game_name"] == game]["summary"].iloc[0])
st.caption("Written by Claude from each game's prediction.")