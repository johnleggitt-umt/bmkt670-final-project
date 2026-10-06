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

Source	What it provides	Access
| Steamworks (partner.steamgames.com/doc/home)| Official dev tools from Steam. API includes information like release date, Metacritic rating, and much more | Free API key; satisfies the course's live API-access requirement |
| Steam Charts (steamcharts.com) | Third party source that provides an “ongoing analysis of Steam’s concurrent players”, including historical concurrent player data | Public HTML tables, can be scraped with a Python program (or there’s a dataset on Kaggle as a backup) |
| Steam Spy (steamspy.com) | Third party source with details about Steam games not available in official API, such as user tags and playtime | Free API access, no API key required |


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