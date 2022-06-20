create or replace table movies_metadata (
  budget int,	
  genres string,
  homepage string,
  id int,
  imdb_id string,
  original_language	string,
  original_title string,
  overview string,
  popularity float,
  poster_path string,
  production_companies string,
  production_countries string,
  release_date date,
  revenue int,
  runtime int,
  spoken_languages string,
  status_released string,
  tagline string,
  title string,
  video	string,
  vote_average float
);

CREATE OR REPLACE TABLE CREDITS (
CAST varchar,
DIRECTOR varchar,
ID integer
);

CREATE OR REPLACE TABLE KEYWORDS (
ID integer,
KEYWORDS varchar
);