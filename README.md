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
1. Create and activate a virtual environment
2. Install packages: pip install -r requirements.txt
3. Create a .env file with your API keys and DB_PASSWORD 
4. Pull the data: run each script in etl/ in numerical number (e.g. extract_1.py first, extract_2.py second, etc.)
5. Build the database: run sql/schema.sql in pgAdmin or psql
6. Confirm it worked: python db_check.py (should print all table names)


## AI Usage
Claude (Anthropic) was used to explain how the Steam Store API, SteamSpy API, and SteamCharts pages are structured, to help write and debug the extract scripts (requests, JSON handling, BeautifulSoup parsing, and error handling), and to review the schema and field-source documentation.