DROP TABLE IF EXISTS dim_game CASCADE;
DROP TABLE IF EXISTS dim_user_tag CASCADE;
DROP TABLE IF EXISTS dim_month CASCADE;
DROP TABLE IF EXISTS fact_user_tag CASCADE;
DROP TABLE IF EXISTS fact_monthly_players CASCADE;
DROP TABLE IF EXISTS ml_features_player_retention CASCADE;

-- one row = one game
CREATE TABLE dim_game (
	app_id			INTEGER			PRIMARY KEY,
	game_name		TEXT			NOT NULL,
	release_date	DATE			NOT NULL,
	initial_cost	NUMERIC(5,2)	NOT NULL
);

-- one row = one user tag
CREATE TABLE dim_user_tag (
	user_tag_id 	INTEGER			PRIMARY KEY,
	tag_name		TEXT			NOT NULL
);

-- one row = one month/year
CREATE TABLE dim_month (
	month_id	 	DATE			PRIMARY KEY,
	year_num		INTEGER			NOT NULL,
	month_num		INTEGER			NOT NULL CHECK (month_num >= 1 AND month_num <= 12)
);

-- one row = one user tag per one game
CREATE TABLE fact_user_tag (
	app_id			INTEGER			NOT NULL,
	user_tag_id 	INTEGER			NOT NULL,
	user_tag_votes	INTEGER			NOT NULL,
	PRIMARY KEY		(app_id, user_tag_id),
	FOREIGN KEY		(app_id)		REFERENCES dim_game(app_id),
	FOREIGN KEY		(user_tag_id)	REFERENCES dim_user_tag(user_tag_id)
);

-- one row = one month of player counts per one game
CREATE TABLE fact_monthly_players (
	app_id			INTEGER			NOT NULL,
	month_id	 	DATE			NOT NULL,
	avg_players		NUMERIC(10,2) 	NOT NULL,
	peak_players	INTEGER			NOT NULL,
	months_released	INTEGER			NOT NULL,
	PRIMARY KEY		(app_id, month_id),
	FOREIGN KEY		(app_id)		REFERENCES dim_game(app_id),
	FOREIGN KEY		(month_id)		REFERENCES dim_month(month_id)
);

-- one row = one game
CREATE TABLE ml_features_player_retention (
	app_id					INTEGER			PRIMARY KEY,
	release_year			INTEGER			NOT NULL,
	initial_cost			NUMERIC(5,2)	NOT NULL,
	month1_avg_players		NUMERIC(10,2)	NOT NULL,
	month1_peak_players 	INTEGER			NOT NULL,
	month12_avg_players		NUMERIC(10,2)	NOT NULL,
	month36_avg_players		NUMERIC(10,2)	NOT NULL,
	m1_to_m12_retention		NUMERIC			NOT NULL,
	m1_peak_m1_avg_ratio	NUMERIC			NOT NULL,
	tag_singleplayer		INTEGER			NOT NULL,
	tag_action				INTEGER			NOT NULL,
	tag_multiplayer			INTEGER			NOT NULL,
	tag_adventure			INTEGER			NOT NULL,
	tag_atmospheric			INTEGER			NOT NULL,
	tag_co_op				INTEGER			NOT NULL,
	tag_open_world			INTEGER			NOT NULL,
	tag_indie				INTEGER			NOT NULL,
	tag_rpg					INTEGER			NOT NULL,
	tag_first_person		INTEGER			NOT NULL,
	split					TEXT			NOT NULL CHECK (split IN ('train', 'validate', 'test')),
	FOREIGN KEY				(app_id)		REFERENCES dim_game(app_id)
	);
