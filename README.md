One row in my ML feature table = one ___.

# [Your Project Title]

## Business Question
[One sentence from your proposal]

## Target Variable
[The single thing your model predicts]

## Prediction Unit
One row in my ML feature table = one [game / store-week / flight].

## Data Sources
| Source | What it provides | Access |
|---|---|---|  

[For hand-downloaded files, list the URL, date downloaded, and the clicks or filters you used.]

## How to Run
1. Create and activate a virtual environment
2. Install packages: pip install -r requirements.txt
3. Create a .env file with your API keys and DB_PASSWORD 
4. Pull the data: run each script in etl/ (e.g., python etl/extract_games.py)  
5. Build the database: run sql/schema.sql in pgAdmin or psql
6. Confirm it worked: python db_check.py (should print all table names)


## AI Usage
[Which AI tools you used and for which parts]