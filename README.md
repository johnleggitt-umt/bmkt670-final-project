# Predicting Long-Term Player Retention on Steam

## Business Question
How many people will still be playing a video game on Steam three years after its release?

## Target Variable
Average concurrent players of a game three years after release

## Prediction Unit
One row in my ML feature table = one video game.

## Data Sources
| Source | What it provides | Access |
|---|---|---|  
| Steamworks (partner.steamgames.com/doc/home)| Official dev tools from Steam. API includes information like release date, Metacritic rating, and much more | Free API access, no API key required (for the data used in this project) |
| Steam Charts (steamcharts.com) | Third party source that provides an “ongoing analysis of Steam’s concurrent players”, including historical concurrent player data | Public HTML tables, can be scraped with a Python program (or there’s a dataset on Kaggle as a backup) |
| Steam Spy (steamspy.com) | Third party source with details about Steam games not available in official API, such as user tags and playtime | Free API access, no API key required |


## How to Run
1. Create and activate a virtual environment.
2. Install packages: pip install -r requirements.txt.
3. Build the database: create empty daatabase and run sql/schema.sql in pgAdmin.
4. Create a .env file with your PGHOST, PGPORT, PGDATABASE, PGUSER, and PGPASSWORD.
5. Run `run_pipeline.py` from the project folder.
    - Runs extract, transform, load, quality checks, and the model, in that order.
    - Extract scripts take hours to run, and they are skipped by default. To pull fresh data, set `run_extract_steps = True` in `run_pipeline.py` .


## AI Usage
Claude (Anthropic) was used to explain how the Steam Store API, SteamSpy API, and SteamCharts pages are structured, to help write and debug the extract scripts (requests, JSON handling, BeautifulSoup parsing, and error handling), and to review the schema and field-source documentation. Additionally, Claude was used to generate that code in `transform.py` that builds the ML Features table from the dimension and fact tables.