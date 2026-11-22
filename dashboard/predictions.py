import os
from pathlib import Path
import warnings
import psycopg2
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
import altair as alt
from sklearn.metrics import mean_absolute_error

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

# Querying and processing data
query = """
    SELECT p.app_id, g.game_name, p.split, p.actual, p.predicted
    FROM predictions p
    JOIN dim_game g ON p.app_id = g.app_id
"""

df = pd.read_sql(query, conn)
conn.close()

train    = df[df["split"] == "train"]
validate = df[df["split"] == "validate"]
test     = df[df["split"] == "test"]

baseline_guess = train["actual"].mean()
baseline_mae = mean_absolute_error(validate["actual"], [baseline_guess] * len(validate))
validate_mae = mean_absolute_error(validate["actual"], validate["predicted"])
test_mae = mean_absolute_error(test["actual"], test["predicted"])

# Creating dashboard page
st.title("How Good are the Predictions?")
st.caption("Compares the model's predictions to what actually happened for games it never learned from: " \
"validate games (released 2020–2021) and test games (2022–2023).")

# KPIs
k1, k2, k3 = st.columns(3)
k1.metric("Baseline MAE (2020-2021)", f"{baseline_mae:,.0f} players")
k2.metric("Model MAE (2020-2021, validate)", f"{validate_mae:,.0f} players")
k3.metric("Model MAE (2022-2023, test)", f"{test_mae:,.0f} players")

# Scatterplot of actual vs predicted
scored = df[df["split"].isin(["validate", "test"])]

st.subheader("Predicted vs. actual players")
points = alt.Chart(scored).mark_circle().encode(
    x=alt.X("actual", scale=alt.Scale(type="log"), title="Actual month 36 players"),
    y=alt.Y("predicted", scale=alt.Scale(type="log"), title="Predicted month 36 players"),
    color=alt.Color("split", scale=alt.Scale(domain=["validate", "test"], range=["#1f77b4", "#ff7f0e"])),
    tooltip=["game_name", "actual", "predicted"]
)

low = min(scored["actual"].min(), scored["predicted"].min())
high = max(scored["actual"].max(), scored["predicted"].max())
line_df = pd.DataFrame({"x": [low, high], "y": [low, high]})

line = alt.Chart(line_df).mark_line(color="gray", strokeDash=[4, 4]).encode(
    x="x",
    y="y"
)

st.altair_chart((points + line).configure_axis(grid=False))
st.caption("Each dot is a video game. Dots on the dashed line were predicted exactly; " \
"dots above it were predicted too high, and dots below it too low. Both axes use a log scale.")

# Table of big misses
df_miss = scored.drop(columns=["app_id"])
df_miss["error"] = df_miss["actual"] - df_miss["predicted"]
df_miss["times_mae"] = df_miss["error"].abs() / test_mae
df_miss["pct_error"] = df_miss["error"].abs() / df_miss["actual"] * 100
df_miss = df_miss.sort_values("times_mae", ascending=False)
df_miss["% error"] = df_miss["pct_error"].map("{:.1f}%".format)
df_miss["x typical miss"] = df_miss["times_mae"].map("{:.1f}x".format)
df_miss["flag"] = (df_miss["times_mae"] > 2).map({True: "unusual", False: ""})
df_miss = df_miss.drop(columns=["pct_error", "times_mae"])
df_miss[["actual", "predicted", "error"]] = df_miss[["actual", "predicted", "error"]].round(0)

st.subheader("Biggest Misses")
st.caption(f"A miss is flagged as unusual when it's more than twice the model's test MAE ({2 * test_mae:,.0f} players). "
           "Because MAE is in players, the largest games dominate this list. % error shows how far off each "
           "prediction was relative to the game's size.")
st.dataframe(df_miss.head(10), hide_index=True)
st.caption("The biggest miss is Battlefield V: the model predicted about 151,000 players at month 36, but only about 9,400 were playing. " \
"Looking at the data, there was a spike in players at month 12, " \
"possibly due to a sale or promotion. Since the model's strongest signal is players at month 12, this spike is likely to have thrown off the prediction. " \
"Sports games are also frequently missed, as they release a new version yearly, and players drop off when that happens.")