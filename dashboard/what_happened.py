import os
from pathlib import Path
import warnings
import psycopg2
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
import altair as alt

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

# Creating dashboard page
st.title("What Happened?")
st.caption("This page shows how player counts changed during the first three years after a video game's launch on Steam."
"Values show the median game's average concurrent players.")


# Querying and processing data and creating filter
query = """
    SELECT f.app_id, f.months_released, f.avg_players, g.release_date
    FROM fact_monthly_players f
    JOIN dim_game g ON f.app_id = g.app_id
    WHERE g.release_date >= '2012-07-01'
"""

df = pd.read_sql(query, conn)
conn.close()

df["release_year"] = pd.to_datetime(df["release_date"]).dt.year

min_year = int(df["release_year"].min())
max_year = int(df["release_year"].max())
years = st.slider("Release year", min_year, max_year, (min_year, max_year))

df = df[(df["release_year"] >= years[0]) & (df["release_year"] <= years[1])]

# KPIs
k1, k2, k3, k4 = st.columns(4)

games = df["app_id"].nunique()
launch = df[df["months_released"] == 0]["avg_players"].median()
month12 = df[df["months_released"] == 12]["avg_players"].median()
month36 = df[df["months_released"] == 36]["avg_players"].median() 

k1.metric("Total games in dataset", f"{games:,}")
k2.metric("Average concurrent players at launch", f"{launch:,.0f}")
k3.metric("Average concurrent players in month 12", f"{month12:,.0f}")
k4.metric("Average concurrent players in month 36", f"{month36:,.0f}")

# Charts
col1, col2 = st.columns(2, gap="large")

# Chart 1: Line graph
with col1:
    st.subheader("How player counts change after release")
    curve = df[df["months_released"].between(0, 36)]
    curve = curve.groupby("months_released")["avg_players"].median()
    st.line_chart(curve, x_label="Months since release", y_label="Average concurrent players")
    st.caption("In general, concurrent players quickly fall after the game launches, but level off at about six months.")

# Chart 2: Scatterplot
with col2:
    st.subheader("Players at one year vs. players at three years")
    scatter = df[df["months_released"].isin([12, 36])]
    scatter = scatter.pivot_table(index="app_id", columns="months_released", values="avg_players")
    scatter = scatter.dropna()
    scatter = scatter.rename(columns={12: "month12", 36: "month36"})
    chart = alt.Chart(scatter).mark_circle().encode(
        x=alt.X("month12", scale=alt.Scale(type="log"), title="Month 12 players"),
        y=alt.Y("month36", scale=alt.Scale(type="log"), title="Month 36 players")
    ).configure_axis(grid=False)
    if "month36" not in scatter.columns:
        st.write("No games in these years have reached month 36 yet.")
    else:
        st.altair_chart(chart)
    st.caption("The number of players at 12 months has a strong postive correlation with the number of players at 36 months.")