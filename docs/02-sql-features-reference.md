# Complex SQL Features Documentation

This document lists all complex SQL features implemented in the Spotify application.

## 1. WITH Clauses (Common Table Expressions - CTEs)

### Example 1: Song Performance Metrics
**File**: `complex_queries.py` - `get_artist_song_performance()`
```sql
WITH SongMetrics AS (
    SELECT song_id, song_name, release_date,
           COUNT(CASE WHEN interaction_type = 'Play' THEN 1 END) AS total_plays,
           ...
    FROM song s
    JOIN song_artist sa ON s.song_id = sa.song_id
    LEFT JOIN song_interaction si ON s.song_id = si.song_id
    WHERE sa.artist_id = %s
    GROUP BY s.song_id, s.song_name, s.release_date
)
SELECT *, 
       (total_likes + total_shares) * 100.0 / total_plays AS engagement_rate
FROM SongMetrics
```

### Example 2: Listener Age Groups
**File**: `complex_queries.py` - `get_artist_age_group_distribution()`
```sql
WITH ListenerAges AS (
    SELECT listener_id, Date_of_birth,
           YEAR(CURDATE()) - YEAR(Date_of_birth) - ... AS age,
           COUNT(interaction_id) AS interaction_count
    FROM listener l
    JOIN song_interaction si ON l.listener_id = si.listener_id
    ...
    GROUP BY listener_id, Date_of_birth
)
SELECT 
    CASE WHEN age < 18 THEN 'Under 18' ... END AS age_group,
    COUNT(DISTINCT listener_id) AS unique_listeners
FROM ListenerAges
GROUP BY age_group
```

### Example 3: Recommendations
**File**: `complex_queries.py` - `get_listener_recommendations()`
```sql
WITH ListenerFavoriteGenre AS (
    SELECT genre, COUNT(interaction_id) AS interaction_count
    FROM song_interaction si
    JOIN song s ON si.song_id = s.song_id
    WHERE si.listener_id = %s
    GROUP BY genre
    ORDER BY interaction_count DESC
    LIMIT 1
),
ListenerPlayedSongs AS (
    SELECT DISTINCT song_id
    FROM song_interaction
    WHERE listener_id = %s
)
SELECT s.song_id, s.song_name, ...
FROM song s
WHERE s.genre = (SELECT genre FROM ListenerFavoriteGenre)
  AND s.song_id NOT IN (SELECT song_id FROM ListenerPlayedSongs)
```

## 2. Subqueries

### Scalar Subquery
**File**: `complex_queries.py` - `get_artist_country_distribution()`
```sql
SELECT country, COUNT(DISTINCT listener_id) AS unique_listeners,
       ROUND(COUNT(DISTINCT listener_id) * 100.0 / (
           SELECT COUNT(DISTINCT l2.listener_id)
           FROM listener l2
           JOIN song_interaction si2 ON l2.listener_id = si2.listener_id
           JOIN song_artist sa2 ON si2.song_id = sa2.song_id
           WHERE sa2.artist_id = %s
       ), 2) AS percentage_of_listeners
FROM listener l
...
```

### IN Subquery (Set Membership)
**File**: `complex_queries.py` - `get_followed_artists_songs()`
```sql
SELECT s.song_id, s.song_name, ...
FROM song s
JOIN song_artist sa ON s.song_id = sa.song_id
WHERE sa.artist_id IN (
    SELECT artist_id 
    FROM follow_artist 
    WHERE listener_id = %s
)
```

### NOT IN Subquery (Set Difference)
**File**: `complex_queries.py` - `get_listeners_who_follow_but_never_interact()`
```sql
SELECT listener_id, listener_name, ...
FROM listener l
JOIN follow_artist fa ON l.listener_id = fa.listener_id
WHERE fa.artist_id = %s
  AND l.listener_id NOT IN (
      SELECT DISTINCT si.listener_id
      FROM song_interaction si
      JOIN song_artist sa ON si.song_id = sa.song_id
      WHERE sa.artist_id = %s
  )
```

## 3. Set Operations

### NOT EXISTS (Set Difference)
**File**: `complex_queries.py` - `get_artists_with_no_interactions()`
```sql
SELECT a.artist_id, a.artist_name, COUNT(DISTINCT sa.song_id) AS total_songs
FROM artist a
JOIN song_artist sa ON a.artist_id = sa.artist_id
WHERE NOT EXISTS (
    SELECT 1
    FROM song_interaction si
    WHERE si.song_id = sa.song_id
)
GROUP BY a.artist_id, a.artist_name
```

## 4. Advanced Aggregate Functions

### Conditional Aggregates with CASE
**File**: `complex_queries.py` - Multiple functions
```sql
COUNT(CASE WHEN si.interaction_type = 'Play' THEN 1 END) AS total_plays,
COUNT(CASE WHEN si.interaction_type = 'Like' THEN 1 END) AS total_likes,
SUM(CASE WHEN si.interaction_type = 'Like' THEN 1 ELSE 0 END) AS total_likes
```

### Window Functions

#### ROW_NUMBER()
**File**: `complex_queries.py` - `get_artist_top_songs()`
```sql
ROW_NUMBER() OVER (ORDER BY COUNT(si.interaction_id) DESC) AS rank_by_interactions
```

#### DENSE_RANK()
**File**: `complex_queries.py` - `get_artist_top_songs()`
```sql
DENSE_RANK() OVER (ORDER BY COUNT(CASE WHEN si.interaction_type = 'Play' THEN 1 END) DESC) AS rank_by_plays
```

#### LAG() Window Function
**File**: `complex_queries.py` - `get_artist_monthly_follower_growth()`
```sql
WITH MonthlyFollows AS (...)
SELECT 
    follow_month,
    new_follows,
    LAG(new_follows, 1, 0) OVER (ORDER BY follow_month) AS previous_month_follows,
    new_follows - LAG(new_follows, 1, 0) OVER (ORDER BY follow_month) AS follow_change,
    CASE 
        WHEN LAG(new_follows, 1, 0) OVER (ORDER BY follow_month) > 0 THEN
            ROUND((new_follows - LAG(...)) * 100.0 / LAG(...), 2)
        ELSE NULL
    END AS growth_percentage
FROM MonthlyFollows
```

### GROUP_CONCAT
**File**: `complex_queries.py` - `get_new_songs()`
```sql
GROUP_CONCAT(CONCAT(a.artist_first_name, ' ', a.artist_last_name) SEPARATOR ', ') AS artists
```

## 5. OLAP Functions

### ROLLUP
**File**: `complex_queries.py` - `get_interactions_by_account_type_and_genre()`
```sql
SELECT 
    lat.account_type,
    s.genre,
    COUNT(si.interaction_id) AS total_interactions,
    COUNT(DISTINCT si.listener_id) AS unique_listeners,
    GROUPING(lat.account_type, s.genre) AS grouping_level
FROM listener_account_type lat
JOIN listener l ON lat.account_id = l.account_id
JOIN song_interaction si ON l.listener_id = si.listener_id
JOIN song s ON si.song_id = s.song_id
GROUP BY lat.account_type, s.genre WITH ROLLUP
ORDER BY lat.account_type, s.genre
```

### CUBE-like Operations (Multi-dimensional Analysis)
**File**: `complex_queries.py` - `get_artist_performance_by_country_and_genre()`
```sql
SELECT 
    l.country,
    s.genre,
    COUNT(si.interaction_id) AS total_interactions,
    COUNT(CASE WHEN si.interaction_type = 'Play' THEN 1 END) AS plays,
    COUNT(CASE WHEN si.interaction_type = 'Like' THEN 1 END) AS likes,
    AVG(s.duration) AS avg_song_duration
FROM listener l
JOIN song_interaction si ON l.listener_id = si.listener_id
JOIN song s ON si.song_id = s.song_id
JOIN song_artist sa ON s.song_id = sa.song_id
WHERE sa.artist_id = %s
GROUP BY l.country, s.genre WITH ROLLUP
ORDER BY l.country, s.genre
```

## 6. Advanced Date Functions

### Date Arithmetic
```sql
DATE_SUB(CURDATE(), INTERVAL 30 DAY)  -- Last 30 days
DATE_SUB(CURDATE(), INTERVAL 7 DAY)   -- Last 7 days
```

### Date Formatting
```sql
DATE_FORMAT(follow_date, '%Y-%m') AS follow_month
```

### Age Calculation
```sql
YEAR(CURDATE()) - YEAR(Date_of_birth) - 
(DATE_FORMAT(CURDATE(), '%m%d') < DATE_FORMAT(Date_of_birth, '%m%d')) AS age
```

## 7. Set Comparison Operations

### Set Membership (IN)
- Used in `get_followed_artists_songs()` to find songs from followed artists

### Set Difference (NOT IN, NOT EXISTS)
- Used in `get_listeners_who_follow_but_never_interact()`
- Used in `get_artists_with_no_interactions()`

## 8. Advanced Calculations

### Percentage Calculations
```sql
ROUND((total_likes + total_shares) * 100.0 / total_plays, 2) AS engagement_rate
ROUND(COUNT(DISTINCT listener_id) * 100.0 / (SELECT COUNT(...)), 2) AS percentage
```

### Growth Percentage
```sql
CASE 
    WHEN previous > 0 THEN
        ROUND((current - previous) * 100.0 / previous, 2)
    ELSE NULL
END AS growth_percentage
```

## Summary

The application implements:
- ✅ **WITH Clauses (CTEs)**: 3+ examples
- ✅ **Subqueries**: Scalar, IN, NOT IN, EXISTS, NOT EXISTS
- ✅ **Set Operations**: Set membership, set difference
- ✅ **Window Functions**: ROW_NUMBER(), DENSE_RANK(), LAG()
- ✅ **OLAP Functions**: ROLLUP, CUBE-like operations
- ✅ **Advanced Aggregates**: Conditional aggregates, GROUP_CONCAT
- ✅ **Date Functions**: Date arithmetic, formatting, age calculations
- ✅ **Complex Calculations**: Percentages, growth rates, engagement metrics

All queries are optimized and use proper indexing for performance.

