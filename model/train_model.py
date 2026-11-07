import os
from pathlib import Path
import warnings
import psycopg2
import pandas as pd
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsRegressor
from psycopg2.extras import execute_values


load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DB_CONFIG = {
    "host": os.getenv("PGHOST"),
    "port": os.getenv("PGPORT"),
    "dbname": os.getenv("PGDATABASE"),
    "user": os.getenv("PGUSER"),
    "password": os.getenv("PGPASSWORD"),
}

warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")

# Load ml table as df and split into train, validate, test
conn = psycopg2.connect(**DB_CONFIG)
df = pd.read_sql("SELECT * FROM ml_features_player_retention", conn)
conn.close()

train    = df[df["split"] == "train"]
validate = df[df["split"] == "validate"]
test     = df[df["split"] == "test"]

print("ml_features_player_retention splits:")
print(f"{len(train)} rows of train data")
print(f"{len(validate)} rows of validate data")
print(f"{len(test)} rows of test data")
print("")

# Create plots of training data
# Histogram of month36_avg_players
plt.hist(train["month36_avg_players"], bins=30)
plt.yscale("log")
plt.title("Average players at month 36")
plt.xlabel("Average concurrent players")
plt.ylabel("Number of games")
plt.savefig("docs/figures/target_histogram.png")
plt.close()

# Scatter plot of month12_avg_players vs. month36_avg_players
plt.scatter(train["month12_avg_players"], train["month36_avg_players"], alpha=0.5)
plt.xscale("log")
plt.yscale("log")
plt.title("Month 12 players vs. month 36 players")
plt.xlabel("Average players at month 12 (log scale)")
plt.ylabel("Average players at month 36 (log scale)")
plt.savefig("docs/figures/month12_vs_target.png")
plt.close()

# Scatter plot of m1_to_m12_retention vs. month36_avg_players
plt.scatter(train["m1_to_m12_retention"], train["month36_avg_players"], alpha=0.5)
plt.xscale("log")
plt.yscale("log")
plt.title("First-year retention vs. month 36 players")
plt.xlabel("Month 12 players ÷ month 1 players")
plt.ylabel("Average players at month 36 (log scale)")
plt.savefig("docs/figures/retention_vs_target.png")
plt.close()

# Calculate mean absolute error as baseline
baseline_guess = train["month36_avg_players"].mean()
baseline_mae = mean_absolute_error(validate["month36_avg_players"], [baseline_guess] * len(validate))
print("Baseline (train average, scored on validate):")
print(f"Baseline MAE: {baseline_mae:,.0f} players")
print("")

# Splitting predictors and target

x_train = train.drop(columns=["app_id", "split", "month36_avg_players"])
y_train = train["month36_avg_players"]

x_validate = validate.drop(columns=["app_id", "split", "month36_avg_players"])
y_validate = validate["month36_avg_players"]


# Linear regression model
lin_reg = LinearRegression()
lin_reg.fit(x_train, y_train)

y_pred_train_lin = lin_reg.predict(x_train)
y_pred_validate_lin = lin_reg.predict(x_validate)

print("Linear Regression Model:")
print(f"Linear regression train MAE: {mean_absolute_error(y_train, y_pred_train_lin):,.0f} players")
print(f"Linear regression validate MAE: {mean_absolute_error(y_validate, y_pred_validate_lin):,.0f} players")
print("")


# Random forest model
forest = RandomForestRegressor(random_state=42)
forest.fit(x_train, y_train)

y_pred_train_forest = forest.predict(x_train)
y_pred_validate_forest = forest.predict(x_validate)

print("Random Forest Model:")
print(f"Random forest train MAE: {mean_absolute_error(y_train, y_pred_train_forest):,.0f} players")
print(f"Random forest validate MAE: {mean_absolute_error(y_validate, y_pred_validate_forest):,.0f} players")
print("")


# KNN model
standard_scaler = StandardScaler()
standard_scaler.fit(x_train)
x_train_knn = standard_scaler.transform(x_train)
x_validate_knn = standard_scaler.transform(x_validate)

knn = KNeighborsRegressor()
knn.fit(x_train_knn, y_train)

y_pred_train_knn = knn.predict(x_train_knn)
y_pred_validate_knn = knn.predict(x_validate_knn)

print("KNN Model:")
print(f"KNN train MAE: {mean_absolute_error(y_train, y_pred_train_knn):,.0f} players")
print(f"KNN validate MAE: {mean_absolute_error(y_validate, y_pred_validate_knn):,.0f} players")
print("")


# Forest model on test data
x_test = test.drop(columns=["app_id", "split", "month36_avg_players"])
y_test = test["month36_avg_players"]

y_pred_test_forest = forest.predict(x_test)
print("Random forest has the lowest validate MAE compared to baseline. Ran random forest on test data:")
print(f"Random forest test MAE: {mean_absolute_error(y_test, y_pred_test_forest):,.0f} players")
print("")

importances = pd.Series(forest.feature_importances_, index=x_train.columns)

print("Top Five Features of Random Forest Model:")
print(importances.sort_values(ascending=False).head())
print("")

# Creating Predictions table in Database

df["predicted"] = forest.predict(df.drop(columns=["app_id", "split", "month36_avg_players"]))
predictions = df[["app_id", "split", "month36_avg_players", "predicted"]]
predictions = predictions.rename(columns={"month36_avg_players": "actual"})
predictions["error"] = predictions["actual"] - predictions["predicted"]
predictions["model_name"] = "random_forest"

predictions.to_csv("data/clean/predictions.csv", index=False)
print("predictions saved as data/clean/predictions.csv:")
print("")

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

cur.execute("TRUNCATE predictions CASCADE")

predictions = pd.read_csv("data/clean/predictions.csv")
execute_values(cur, f"INSERT INTO predictions VALUES %s", predictions.values.tolist())

conn.commit()
conn.close()

print(f"Saved {len(predictions)} predictions to the predictions table")