DROP TABLE IF EXISTS dim_game CASCADE;
DROP TABLE IF EXISTS dim_user_tag CASCADE;
DROP TABLE IF EXISTS dim_month CASCADE;
DROP TABLE IF EXISTS fact_user_tag CASCADE;
DROP TABLE IF EXISTS fact_monthly_players CASCADE;


CREATE TABLE dim_game (
	app_id			INTEGER			PRIMARY KEY,
	game_name		TEXT			NOT NULL,
	developer		TEXT			NOT NULL,
	release_date	DATE			NOT NULL CHECK (release_date >= '2012-07-01'),
	initial_cost	NUMERIC(5,2)	NOT NULL CHECK (initial_cost >= 0),
	store_category	TEXT			NOT NULL
);

CREATE TABLE dim_user_tag (
	user_tag_id 	INTEGER			PRIMARY KEY,
	tag_name		TEXT			NOT NULL
);

CREATE TABLE dim_month (
	month_id	 	DATE			PRIMARY KEY,
	year_num		INTEGER			NOT NULL,
	month_num		INTEGER			NOT NULL CHECK (month_num >= 1 AND month_num <= 12)
);

CREATE TABLE fact_user_tag (
	app_id			INTEGER			NOT NULL,
	user_tag_id 	INTEGER			NOT NULL,
	user_tag_votes	INTEGER			NOT NULL,
	PRIMARY KEY		(app_id, user_tag_id),
	FOREIGN KEY		(app_id)		REFERENCES dim_game(app_id),
	FOREIGN KEY		(user_tag_id)	REFERENCES dim_user_tag(user_tag_id)
);

CREATE TABLE fact_monthly_players (
	app_id			INTEGER			NOT NULL,
	month_id	 	DATE			NOT NULL,
	avg_players		NUMERIC(10,2) 	NOT NULL,
	peak_players	INTEGER			NOT NULL,
	PRIMARY KEY		(app_id, month_id),
	FOREIGN KEY		(app_id)		REFERENCES dim_game(app_id),
	FOREIGN KEY		(month_id)		REFERENCES dim_month(month_id)
)