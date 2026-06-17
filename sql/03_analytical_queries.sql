
-- Repository: Spotify project database (tables: artist, song, song_artist, song_interaction,
-- listener, follow_artist, listener_account_type, etc.)
-- This file contains 17 queries. For each query:
-- 1) Description / explanation
-- 2) SQL statement (MySQL dialect)
-- 3) output
-- 4) Functions used 
-- NOTE: I have applied limit of 10 to some queries to keep output manageable in length.

USE spotify_db;

-- Query #1: Top Most Played Songs by an Artist
-- Description: Finds the total number of 'Play' interactions for each song released by a specific artist (e.g., Artist ID = 1) and the most played songs.
-- Function Used: Basic Aggregation (COUNT, GROUP BY), JOIN, LIMIT.
-- SQL Statement:

use spotify_db;

SELECT
A.artist_first_name, A.artist_last_name, S.song_name, COUNT(SI.interaction_id) AS total_plays
FROM artist A
JOIN song_artist SA ON A.artist_id = SA.artist_id
JOIN song S ON SA.song_id = S.song_id
JOIN song_interaction SI ON S.song_id = SI.song_id
WHERE A.artist_id = 2 AND SI.interaction_type = 'Play' -- -- Arijit Singh artist_id is 2 , change artist id here for different artist
GROUP BY S.song_id, S.song_name
ORDER BY total_plays DESC
LIMIT 1;

--  Output
-- +-- -- -- -- -- -- -- -- -- -+-- -- -- -- -- -- -- -- -- +-- -- -- -- -- -- -- -+-- -- -- -- -- -- -+
-- | artist_first_name | artist_last_name | song_name     | total_plays |
-- +-- -- -- -- -- -- -- -- -- -+-- -- -- -- -- -- -- -- -- +-- -- -- -- -- -- -- -+-- -- -- -- -- -- -+
-- | Arijit            | Singh            | Channa Mereya |           3 |
-- +-- -- -- -- -- -- -- -- -- -+-- -- -- -- -- -- -- -- -- +-- -- -- -- -- -- -- -+-- -- -- -- -- -- -+

 


-- Query #2: Monthly Follower Growth (Advanced)
-- Description: Calculates the number of new followers an artist gained each month and compares it to the previous month's total to show growth or decline.
-- This uses the advanced LAG window function.
-- Function Used: Advanced Window Function (LAG), CTE, Date Functions (STRFTIME), Aggregation (COUNT).
-- SQL Statement:
WITH MonthlyFollows AS (
SELECT
YEAR(follow_date) AS follow_year,
MONTH(follow_date) AS follow_month,
COUNT(listener_id) AS new_follows
FROM FOLLOW_ARTIST
WHERE artist_id = 2 -- -- Arijit Singh artist_id is 2 , change artist id here for different artist
GROUP BY 1, 2)
SELECT
follow_year,
follow_month,
new_follows,
LAG(new_follows, 1, 0) OVER (ORDER BY follow_year, follow_month) AS previous_month_follows,
new_follows - LAG(new_follows, 1, 0) OVER (ORDER BY follow_year, follow_month) AS follow_change
FROM MonthlyFollows
ORDER BY follow_year DESC, follow_month DESC;

-- Output:
-- +-------------+--------------+-------------+------------------------+---------------+
-- | follow_year | follow_month | new_follows | previous_month_follows | follow_change |
-- +-------------+--------------+-------------+------------------------+---------------+
-- |        2025 |           12 |           1 |                      1 |             0 |
-- |        2024 |            5 |           1 |                      2 |            -1 |
-- |        2023 |            7 |           2 |                      1 |             1 |
-- |        2023 |            3 |           1 |                      1 |             0 |
-- |        2023 |            1 |           1 |                      0 |             1 |
-- +-------------+--------------+-------------+------------------------+---------------+

 


-- Query #3: Song Engagement Rate Ranking (Advanced)
-- Description: Ranks a specific artist's songs based on an "Engagement Rate" (Likes + Shares / Total Plays).
-- It uses the advanced DENSE_RANK window function to partition the ranking by the artist's genre.
-- Function Used: Advanced Window Function (DENSE_RANK, PARTITION BY), Aggregation (SUM, CASE), CTE.
-- SQL Statement/Commands:
WITH SongMetrics AS (
SELECT
A.artist_id, S.song_id, A.genre,
SUM(CASE WHEN SI.interaction_type = 'Play' THEN 1 ELSE 0 END) AS TotalPlays,
SUM(CASE WHEN SI.interaction_type IN ('Like', 'Share') THEN 1 ELSE 0 END) AS TotalEngagements
FROM ARTIST A
JOIN SONG_ARTIST SA ON A.artist_id = SA.artist_id
JOIN SONG_INTERACTION SI ON SA.song_id = SI.song_id
JOIN SONG S ON SA.song_id = S.song_id
WHERE A.artist_id = 2 -- -- Arijit Singh artist_id is 2 , change artist id here for different artist
GROUP BY A.artist_id, S.song_id, A.genre
)
SELECT
T1.*,
CAST(T1.TotalEngagements AS REAL) * 100 / T1.TotalPlays AS EngagementRate,
DENSE_RANK() OVER (PARTITION BY T1.genre ORDER BY (CAST(T1.TotalEngagements AS REAL) * 100 / T1.TotalPlays) DESC) AS GenreEngagementRank
FROM SongMetrics T1;

--  Output:
-- +-----------+---------+---------------+------------+------------------+----------------+---------------------+
-- | artist_id | song_id | genre         | TotalPlays | TotalEngagements | EngagementRate | GenreEngagementRank |
-- +-----------+---------+---------------+------------+------------------+----------------+---------------------+
-- |         2 |       8 | Bollywood/Pop |          1 |                2 |            200 |                   1 |
-- |         2 |      14 | Bollywood/Pop |          4 |                1 |             25 |                   2 |
-- |         2 |      10 | Bollywood/Pop |          3 |                0 |              0 |                   3 |
-- |         2 |      12 | Bollywood/Pop |          1 |                0 |              0 |                   3 |
-- |         2 |       7 | Bollywood/Pop |          0 |                3 |           NULL |                   4 |
-- +-----------+---------+---------------+------------+------------------+----------------+---------------------+



-- Query #4: Most Skipped Songs
-- Description: Identifies the top 5 songs with the highest count of 'skip' interactions across the entire platform. 
-- SQL Statement/Commands:
SELECT S.song_name, COUNT(SI.interaction_id) AS total_skips
FROM SONG S
JOIN SONG_INTERACTION SI ON S.song_id = SI.song_id
WHERE SI.interaction_type = 'skip'
GROUP BY S.song_id, S.song_name
ORDER BY total_skips DESC
limit 5;

--  Output:
-- +----------------------+-------------+
-- | song_name            | total_skips |
-- +----------------------+-------------+
-- | Despacito (Original) |           6 |
-- | Born This Way        |           6 |
-- | Tera Yaar Hoon Main  |           3 |
-- | Ojitos Lindos        |           3 |
-- | Enemy                |           3 |
-- +----------------------+-------------+




-- Query 5: Top 5 Most Played Songs (Basic aggregation)
-- Description: Find the top 5 songs platform-wide by number of 'Play' interactions.
-- Function used: JOIN, COUNT, GROUP BY, ORDER BY, LIMIT
SELECT
	s.song_id,
	s.song_name,
	GROUP_CONCAT(DISTINCT CONCAT(a.artist_first_name, ' ', a.artist_last_name) SEPARATOR ', ') AS artists,
	COUNT(CASE WHEN si.interaction_type = 'Play' THEN 1 END) AS total_plays
FROM song s
JOIN song_artist sa ON s.song_id = sa.song_id
JOIN artist a ON sa.artist_id = a.artist_id
LEFT JOIN song_interaction si ON s.song_id = si.song_id
GROUP BY s.song_id, s.song_name
ORDER BY total_plays DESC
LIMIT 5;
--  output:
-- +---------+----------------------+--------------+-------------+
-- | song_id | song_name            | artists      | total_plays |
-- +---------+----------------------+--------------+-------------+
-- |      52 | Ojitos Lindos        | Dua Lipa     |           9 |
-- |     155 | Marry You            | Bruno Mars   |           6 |
-- |       3 | Perfect              | Ed Sheeran   |           6 |
-- |     161 | Locked Out of Heaven | Bruno Mars   |           6 |
-- |      15 | Dil Diyan Gallan     | Taylor Swift |           6 |
-- +---------+----------------------+--------------+-------------+




-- Query 6: Artist's Longest and Shortest Song (Union)
-- Description: Return longest and shortest songs for a given artist
(SELECT s.song_id, s.song_name, s.duration, 'Longest' AS kind
 FROM song s
 JOIN song_artist sa ON s.song_id = sa.song_id
 WHERE sa.artist_id = 2
 ORDER BY s.duration DESC
 LIMIT 1)
UNION ALL
(SELECT s.song_id, s.song_name, s.duration, 'Shortest' AS kind
 FROM song s
 JOIN song_artist sa ON s.song_id = sa.song_id
 WHERE sa.artist_id = 2
 ORDER BY s.duration ASC
 LIMIT 1);

--  output:
-- +---------+---------------+----------+----------+
-- | song_id | song_name     | duration | kind     |
-- +---------+---------------+----------+----------+
-- |      10 | Channa Mereya |      289 | Longest  |
-- |     192 | 12            |       12 | Shortest |
-- +---------+---------------+----------+----------+



-- Query 7: listner Account Type summary (OLAP: ROLLUP)
-- Description: Use aggregarion functions
	lat.account_type,
	COUNT(l.listener_id) AS total_listeners
FROM listener_account_type lat
JOIN listener l ON lat.account_id = l.account_id
GROUP BY lat.account_type;

--  output:
-- +--------------+-----------------+
-- | account_type | total_listeners |
-- +--------------+-----------------+
-- | Free         |              14 |
-- | Family       |              42 |
-- | Student      |              25 |
-- | Individual   |              29 |
-- | Duo          |              20 |
-- +--------------+-----------------+


-- Query 8: Average Song Duration by Country and Genre (OLAP: CUBE)
-- Description: Use CUBE to get averages for each country, genre, and their combinations
SELECT
	a.country,
	s.genre,
	ROUND(AVG(s.duration), 2) AS avg_duration_seconds
FROM artist a
JOIN song_artist sa ON a.artist_id = sa.artist_id
JOIN song s ON sa.song_id = s.song_id
WHERE a.country = 'India'
GROUP BY a.country, s.genre
ORDER BY a.country , s.genre;

--  output:
-- +---------+----------------------+----------------------+
-- | country | genre                | avg_duration_seconds |
-- +---------+----------------------+----------------------+
-- | India   |                      |               200.00 |
-- | India   | 12                   |                12.00 |
-- | India   | Bollywood            |               210.00 |
-- | India   | Bollywood Ballad     |               288.00 |
-- | India   | Bollywood Friendship |               266.00 |
-- | India   | Bollywood Party      |               211.00 |
-- | India   | Bollywood Pop        |               270.00 |
-- | India   | Bollywood Romantic   |               261.67 |
-- | India   | Bollywood Sad        |               289.00 |
-- | India   | hit                  |               200.00 |
-- | India   | Romantic             |               230.00 |
-- +---------+----------------------+----------------------+





-- Query 9: Listener Retention Cohort (Quarter of join)
-- Description: Group listeners by the quarter they joined and count their total interactions
SELECT
	CONCAT(YEAR(l.join_date), '-Q', LPAD(QUARTER(l.join_date),1,'0')) AS join_quarter,
	COUNT(DISTINCT l.listener_id) AS total_joined,
	COUNT(si.interaction_id) AS total_interactions
FROM listener l
LEFT JOIN song_interaction si ON l.listener_id = si.listener_id
GROUP BY join_quarter
ORDER BY join_quarter;
--  output:
-- +--------------+--------------+--------------------+
-- | join_quarter | total_joined | total_interactions |
-- +--------------+--------------+--------------------+
-- | 2021-Q1      |            1 |                 20 |
-- | 2022-Q2      |           14 |                 26 |
-- | 2022-Q3      |            8 |                 14 |
-- | 2022-Q4      |           18 |                 27 |
-- | 2023-Q1      |            9 |                 11 |
-- | 2023-Q2      |           11 |                 21 |
-- | 2023-Q3      |           17 |                 23 |
-- | 2023-Q4      |           13 |                 25 |
-- | 2024-Q1      |           24 |                 44 |
-- | 2024-Q2      |           15 |                 28 |
-- +--------------+--------------+--------------------+



-- Query 10: Top 5 Artists by Total Plays (CTE + aggregation)
-- Description: Rank artists by total 'Play' interactions
WITH artist_plays AS (
	SELECT
		a.artist_id,
		a.artist_first_name as artist_first_name,
        a.artist_last_name AS  artist_last_name,
		COUNT(CASE WHEN si.interaction_type = 'Play' THEN 1 END) AS total_plays
	FROM artist a
	JOIN song_artist sa ON a.artist_id = sa.artist_id
	JOIN song_interaction si ON sa.song_id = si.song_id
	GROUP BY a.artist_id, a.artist_first_name, a.artist_last_name
)
SELECT * FROM artist_plays
ORDER BY total_plays DESC
LIMIT 5;
--  output:
-- +-----------+-------------------+------------------+-------------+
-- | artist_id | artist_first_name | artist_last_name | total_plays |
-- +-----------+-------------------+------------------+-------------+
-- |        22 | Bruno             | Mars             |          13 |
-- |         3 | Taylor            | Swift            |          12 |
-- |        20 | Karol             | G                |          11 |
-- |         1 | Ed                | Sheeran          |          10 |
-- |        25 | Glass             | Animals          |           9 |
-- +-----------+-------------------+------------------+-------------+



-- Query 11: Favorite Genre per Listener (ROW_NUMBER)
-- Description: For each listener, compute their favorite genre by interaction count
WITH genre_counts AS (
	SELECT
		l.listener_id,
		s.genre,
		COUNT(*) AS interactions
	FROM song_interaction si
	JOIN song s ON si.song_id = s.song_id
	JOIN listener l ON si.listener_id = l.listener_id
	WHERE s.genre IS NOT NULL
	GROUP BY l.listener_id, s.genre
)
SELECT listener_id, genre AS favorite_genre, interactions
FROM (
	SELECT
		gc.*,
		ROW_NUMBER() OVER (PARTITION BY gc.listener_id ORDER BY gc.interactions DESC) AS rn
	FROM genre_counts gc
) t
WHERE rn = 1
LIMIT 10;
--  output:
-- +-------------+--------------------+--------------+
-- | listener_id | favorite_genre     | interactions |
-- +-------------+--------------------+--------------+
-- |           1 | Indie Pop          |            1 |
-- |           2 | Electropop         |            1 |
-- |           3 | Reggaeton          |            1 |
-- |           4 | Dance-Pop          |            1 |
-- |           5 | Alt Rock           |            2 |
-- |           6 | Pop                |            1 |
-- |           7 | Reggaeton          |            1 |
-- |           8 | R&B                |            1 |
-- |           9 | Bollywood Romantic |            1 |
-- |          10 | Reggaeton          |            2 |
-- +-------------+--------------------+--------------+


-- Query 12: Top Songs with Artist List
-- Description: List top songs with concatenated artist names and a dense rank by interactions

SELECT
	s.song_id,
	s.song_name,
	COALESCE(al.artists, '') AS artists,
	COALESCE(sc.interactions, 0) AS interactions,
	DENSE_RANK() OVER (ORDER BY COALESCE(sc.interactions, 0) DESC) AS rank_by_interactions
FROM song s
LEFT JOIN (
	SELECT sa.song_id,
		   GROUP_CONCAT(CONCAT(a.artist_first_name, ' ', a.artist_last_name) SEPARATOR ', ') AS artists
	FROM song_artist sa
	JOIN artist a ON sa.artist_id = a.artist_id
	GROUP BY sa.song_id
) al ON s.song_id = al.song_id
LEFT JOIN (
	SELECT si.song_id,
		   COUNT(*) AS interactions
	FROM song_interaction si
	WHERE si.interaction_type <> 'Skip'
	GROUP BY si.song_id
) sc ON s.song_id = sc.song_id
ORDER BY interactions DESC
LIMIT 10;

--  output:
-- +---------+-----------------------------+-----------------+--------------+----------------------+
-- | song_id | song_name                   | artists         | interactions | rank_by_interactions |
-- +---------+-----------------------------+-----------------+--------------+----------------------+
-- |     107 | Enemy                       | Coldplay        |           13 |                    1 |
-- |       3 | Perfect                     | Ed Sheeran      |            9 |                    2 |
-- |      52 | Ojitos Lindos               | Dua Lipa        |            9 |                    2 |
-- |      68 | No Tears Left to Cry        | Billie Eilish   |            9 |                    2 |
-- |      17 | Love Story                  | Taylor Swift    |            7 |                    3 |
-- |     126 | Mi Cama                     | Imagine Dragons |            7 |                    3 |
-- |     155 | Marry You                   | Bruno Mars      |            7 |                    3 |
-- |      15 | Dil Diyan Gallan            | Taylor Swift    |            6 |                    4 |
-- |     100 | Always Remember Us This Way | Kendrick Lamar  |            6 |                    4 |
-- |     111 | Need to Know                | Coldplay        |            6 |                    4 |
-- +---------+-----------------------------+-----------------+--------------+----------------------+


-- Query 13: Global Popularity with NTILE Buckets
-- Description: Divide songs into 4 popularity quartiles using NTILE based on interaction count
WITH song_pop AS (
	SELECT
		s.song_id,
		s.song_name,
		COUNT(si.interaction_id) AS interactions
	FROM song s
	LEFT JOIN song_interaction si ON s.song_id = si.song_id
	GROUP BY s.song_id, s.song_name
)
SELECT *, NTILE(4) OVER (ORDER BY interactions DESC) AS quartile
FROM song_pop
ORDER BY interactions DESC
LIMIT 10;


--  output:
-- +---------+----------------------+--------------+----------+
-- | song_id | song_name            | interactions | quartile |
-- +---------+----------------------+--------------+----------+
-- |     107 | Enemy                |           16 |        1 |
-- |      52 | Ojitos Lindos        |           12 |        1 |
-- |     171 | Despacito (Original) |           11 |        1 |
-- |      68 | No Tears Left to Cry |           10 |        1 |
-- |       3 | Perfect              |            9 |        1 |
-- |     131 | Boombayah            |            9 |        1 |
-- |     161 | Locked Out of Heaven |            9 |        1 |
-- |      14 | Tera Yaar Hoon Main  |            8 |        1 |
-- |     155 | Marry You            |            8 |        1 |
-- |      17 | Love Story           |            7 |        1 |
-- +---------+----------------------+--------------+----------+



-- Query 14: Songs Released in Last 30 Days 
-- Description: Get recently released songs with artist names and interaction counts
SELECT
	s.song_id,
	s.song_name,
	s.release_date,
	GROUP_CONCAT(DISTINCT CONCAT(a.artist_first_name, ' ', a.artist_last_name) SEPARATOR ', ') AS artists,
	COUNT(si.interaction_id) AS interaction_count
FROM song s
JOIN song_artist sa ON s.song_id = sa.song_id
JOIN artist a ON sa.artist_id = a.artist_id
LEFT JOIN song_interaction si ON s.song_id = si.song_id
WHERE s.release_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY s.song_id, s.song_name, s.release_date
ORDER BY s.release_date DESC, interaction_count DESC
LIMIT 10;
--  output:
-- +---------+-----------+--------------+--------------+-------------------+
-- | song_id | song_name | release_date | artists      | interaction_count |
-- +---------+-----------+--------------+--------------+-------------------+
-- |     197 | I like    | 2025-12-21   | Arijit Singh |                 0 |
-- |     196 | yes       | 2025-12-06   | Arijit Singh |                 0 |
-- |     198 | Yes       | 2025-12-03   | Arijit Singh |                 0 |
-- |     193 | new life  | 2025-12-01   | Arijit Singh |                 0 |
-- |     194 | hi        | 2025-12-01   | Arijit Singh |                 0 |
-- +---------+-----------+--------------+--------------+-------------------+

-- Query 15: Listener-level Engagement Summary (Pivot-like using SUM with CASE)
-- Description: For a listener, summarize interaction counts by type
SELECT
	l.listener_id,
	l.listener_first_name,
	SUM(CASE WHEN si.interaction_type = 'Play' THEN 1 ELSE 0 END) AS plays,
	SUM(CASE WHEN si.interaction_type = 'Like' THEN 1 ELSE 0 END) AS likes,
	SUM(CASE WHEN si.interaction_type = 'Share' THEN 1 ELSE 0 END) AS shares,
	SUM(CASE WHEN si.interaction_type = 'Skip' THEN 1 ELSE 0 END) AS skips
FROM listener l
LEFT JOIN song_interaction si ON l.listener_id = si.listener_id
GROUP BY l.listener_id, l.listener_first_name;
--  output:
-- +-------------+---------------------+-------+-------+--------+-------+
-- | listener_id | listener_first_name | plays | likes | shares | skips |
-- +-------------+---------------------+-------+-------+--------+-------+
-- +-------------+---------------------+-------+-------+--------+-------+



-- Query 16: Top Artists per Country (RANK partition)
-- Description: For each country, rank artists by follower count and show top 3
WITH artist_follow_counts AS (
  SELECT
    a.artist_id,
    a.artist_first_name,
    a.artist_last_name,
    a.country,
    COUNT(DISTINCT fa.listener_id) AS followers
  FROM artist a
  LEFT JOIN follow_artist fa ON a.artist_id = fa.artist_id
  GROUP BY a.artist_id, a.artist_first_name, a.artist_last_name, a.country
),
ranked AS (
  SELECT
    afc.*,
    RANK() OVER (PARTITION BY afc.country ORDER BY afc.followers DESC) AS country_rank
  FROM artist_follow_counts afc
)
SELECT *
FROM ranked
WHERE country_rank <= 3
ORDER BY country, country_rank
limit 10;
--  output:
-- +-----------+-------------------+------------------+----------------+-----------+--------------+
-- | artist_id | artist_first_name | artist_last_name | country        | followers | country_rank |
-- +-----------+-------------------+------------------+----------------+-----------+--------------+
-- |        10 | Drake             |                  | Canada         |         4 |            1 |
-- |         6 | The               | Weeknd           | Canada         |         4 |            1 |
-- |        19 | Justin            | Bieber           | Canada         |         2 |            3 |
-- |        20 | Karol             | G                | Colombia       |         4 |            1 |
-- |        12 | J Balvin          |                  | Colombia       |         2 |            2 |
-- |         2 | Arijit            | Singh            | India          |         6 |            1 |
-- |        26 | lata              | mangeshkar       | India          |         0 |            2 |
-- |         8 | Bad               | Bunny            | Puerto Rico    |         3 |            1 |
-- |        21 | Blackpink         |                  | South Korea    |         0 |            1 |
-- |         1 | Ed                | Sheeran          | United Kingdom |         5 |            1 |
-- +-----------+-------------------+------------------+----------------+-----------+--------------+

-- Query 17: Interaction Distribution by Hour (Time-series bucketing)
-- Description: Count plays per hour of day to find peak listening hours
SELECT
	HOUR(si.interaction_timestamp) AS hour_of_day,
	COUNT(*) AS plays
FROM song_interaction si
WHERE si.interaction_type = 'Play'
GROUP BY hour_of_day
ORDER BY hour_of_day;
--  output:
-- +-------------+-------+
-- | hour_of_day | plays |
-- +-------------+-------+
-- |           0 |     2 |
-- |           1 |     3 |
-- |           2 |    11 |
-- |           3 |     4 |
-- |           5 |     6 |
-- |           6 |     7 |
-- |           7 |     1 |
-- |           9 |     3 |
-- |          10 |     9 |
-- |          11 |    11 |
-- |          13 |     5 |
-- |          14 |    11 |
-- |          15 |    10 |
-- |          16 |     2 |
-- |          17 |    10 |
-- |          19 |     5 |
-- |          20 |     9 |
-- |          21 |     3 |
-- |          22 |     8 |
-- |          23 |     7 |
-- +-------------+-------+

