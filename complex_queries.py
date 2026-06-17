"""
Complex SQL Queries Module
Implements advanced queries using WITH clauses, subqueries, set operations, OLAP functions
"""

from db_connection import DatabaseConnection
from typing import Optional, List, Dict


class ComplexQueries:
    """Complex SQL queries for analytics and reporting"""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
    
    # ==================== ARTIST DASHBOARD QUERIES ====================
    
    def get_artist_song_performance(self, artist_id: int) -> Optional[List[Dict]]:
        """
        Get detailed performance metrics for all songs by an artist
        Uses WITH clause and advanced aggregates
        """
        query = """
        WITH SongMetrics AS (
            SELECT 
                s.song_id,
                s.song_name,
                s.release_date,
                COUNT(CASE WHEN si.interaction_type = 'Play' THEN 1 END) AS total_plays,
                COUNT(CASE WHEN si.interaction_type = 'Like' THEN 1 END) AS total_likes,
                COUNT(CASE WHEN si.interaction_type = 'Share' THEN 1 END) AS total_shares,
                COUNT(CASE WHEN si.interaction_type = 'Skip' THEN 1 END) AS total_skips,
                COUNT(si.interaction_id) AS total_interactions
            FROM song s
            JOIN song_artist sa ON s.song_id = sa.song_id
            LEFT JOIN song_interaction si ON s.song_id = si.song_id
            WHERE sa.artist_id = %s
            GROUP BY s.song_id, s.song_name, s.release_date
        )
        SELECT 
            song_id,
            song_name,
            release_date,
            total_plays,
            total_likes,
            total_shares,
            total_skips,
            total_interactions,
            CASE 
                WHEN total_plays > 0 THEN 
                    ROUND((CAST(total_likes AS DECIMAL) + total_shares) * 100.0 / total_plays, 2)
                ELSE 0 
            END AS engagement_rate,
            CASE 
                WHEN total_plays > 0 THEN 
                    ROUND(CAST(total_skips AS DECIMAL) * 100.0 / total_plays, 2)
                ELSE 0 
            END AS skip_rate
        FROM SongMetrics
        ORDER BY total_interactions DESC, release_date DESC
        """
        return self.db.execute_query(query, (artist_id,))
    
    def get_artist_follower_count(self, artist_id: int) -> Optional[Dict]:
        """Get total follower count for an artist"""
        query = """
        SELECT 
            COUNT(DISTINCT fa.listener_id) AS total_followers,
            COUNT(DISTINCT CASE WHEN fa.follow_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) 
                THEN fa.listener_id END) AS new_followers_30d,
            COUNT(DISTINCT CASE WHEN fa.follow_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) 
                THEN fa.listener_id END) AS new_followers_7d
        FROM follow_artist fa
        WHERE fa.artist_id = %s
        """
        result = self.db.execute_query(query, (artist_id,))
        return result[0] if result else None
    
    def get_artist_country_distribution(self, artist_id: int) -> Optional[List[Dict]]:
        """
        Get listener distribution by country for an artist
        Uses subquery and advanced aggregates
        """
        query = """
        SELECT 
            l.country,
            COUNT(DISTINCT l.listener_id) AS unique_listeners,
            COUNT(si.interaction_id) AS total_interactions,
            COUNT(CASE WHEN si.interaction_type = 'Play' THEN 1 END) AS total_plays,
            COUNT(CASE WHEN si.interaction_type = 'Like' THEN 1 END) AS total_likes,
            ROUND(COUNT(DISTINCT l.listener_id) * 100.0 / (
                SELECT COUNT(DISTINCT l2.listener_id)
                FROM listener l2
                JOIN song_interaction si2 ON l2.listener_id = si2.listener_id
                JOIN song_artist sa2 ON si2.song_id = sa2.song_id
                WHERE sa2.artist_id = %s
            ), 2) AS percentage_of_listeners
        FROM listener l
        JOIN song_interaction si ON l.listener_id = si.listener_id
        JOIN song_artist sa ON si.song_id = sa.song_id
        WHERE sa.artist_id = %s
        GROUP BY l.country
        ORDER BY unique_listeners DESC, total_interactions DESC
        """
        return self.db.execute_query(query, (artist_id, artist_id))
    
    def get_artist_age_group_distribution(self, artist_id: int) -> Optional[List[Dict]]:
        """
        Get listener distribution by age groups
        Uses CASE expressions and date functions
        """
        query = """
        WITH ListenerAges AS (
            SELECT 
                l.listener_id,
                l.Date_of_birth,
                YEAR(CURDATE()) - YEAR(l.Date_of_birth) - 
                (DATE_FORMAT(CURDATE(), '%m%d') < DATE_FORMAT(l.Date_of_birth, '%m%d')) AS age,
                COUNT(si.interaction_id) AS interaction_count
            FROM listener l
            JOIN song_interaction si ON l.listener_id = si.listener_id
            JOIN song_artist sa ON si.song_id = sa.song_id
            WHERE sa.artist_id = %s AND l.Date_of_birth IS NOT NULL
            GROUP BY l.listener_id, l.Date_of_birth
        )
        SELECT 
            CASE 
                WHEN age < 18 THEN 'Under 18'
                WHEN age BETWEEN 18 AND 24 THEN '18-24'
                WHEN age BETWEEN 25 AND 34 THEN '25-34'
                WHEN age BETWEEN 35 AND 44 THEN '35-44'
                WHEN age BETWEEN 45 AND 54 THEN '45-54'
                WHEN age >= 55 THEN '55+'
                ELSE 'Unknown'
            END AS age_group,
            COUNT(DISTINCT listener_id) AS unique_listeners,
            SUM(interaction_count) AS total_interactions,
            AVG(interaction_count) AS avg_interactions_per_listener
        FROM ListenerAges
        GROUP BY age_group
        ORDER BY 
            CASE age_group
                WHEN 'Under 18' THEN 1
                WHEN '18-24' THEN 2
                WHEN '25-34' THEN 3
                WHEN '35-44' THEN 4
                WHEN '45-54' THEN 5
                WHEN '55+' THEN 6
                ELSE 7
            END
        """
        return self.db.execute_query(query, (artist_id,))
    
    def get_artist_gender_distribution(self, artist_id: int) -> Optional[List[Dict]]:
        """Get listener distribution by gender"""
        query = """
        SELECT 
            l.gender,
            COUNT(DISTINCT l.listener_id) AS unique_listeners,
            COUNT(si.interaction_id) AS total_interactions,
            COUNT(CASE WHEN si.interaction_type = 'Like' THEN 1 END) AS total_likes,
            ROUND(COUNT(CASE WHEN si.interaction_type = 'Like' THEN 1 END) * 100.0 / 
                  NULLIF(COUNT(si.interaction_id), 0), 2) AS like_percentage
        FROM listener l
        JOIN song_interaction si ON l.listener_id = si.listener_id
        JOIN song_artist sa ON si.song_id = sa.song_id
        WHERE sa.artist_id = %s
        GROUP BY l.gender
        ORDER BY unique_listeners DESC
        """
        return self.db.execute_query(query, (artist_id,))
    
    def get_artist_top_songs(self, artist_id: int, limit: int = 10) -> Optional[List[Dict]]:
        """
        Get top performing songs for an artist
        Uses window functions and ranking
        """
        query = """
        WITH SongRankings AS (
            SELECT 
                s.song_id,
                s.song_name,
                s.release_date,
                COUNT(CASE WHEN si.interaction_type = 'Play' THEN 1 END) AS plays,
                COUNT(CASE WHEN si.interaction_type = 'Like' THEN 1 END) AS likes,
                COUNT(CASE WHEN si.interaction_type = 'Share' THEN 1 END) AS shares,
                COUNT(si.interaction_id) AS total_interactions,
                ROW_NUMBER() OVER (ORDER BY COUNT(si.interaction_id) DESC) AS rank_by_interactions,
                DENSE_RANK() OVER (ORDER BY COUNT(CASE WHEN si.interaction_type = 'Play' THEN 1 END) DESC) AS rank_by_plays
            FROM song s
            JOIN song_artist sa ON s.song_id = sa.song_id
            LEFT JOIN song_interaction si ON s.song_id = si.song_id
            WHERE sa.artist_id = %s
            GROUP BY s.song_id, s.song_name, s.release_date
        )
        SELECT 
            song_id,
            song_name,
            release_date,
            plays,
            likes,
            shares,
            total_interactions,
            rank_by_interactions,
            rank_by_plays
        FROM SongRankings
        ORDER BY total_interactions DESC
        LIMIT %s
        """
        return self.db.execute_query(query, (artist_id, limit))
    
    def get_artist_monthly_follower_growth(self, artist_id: int) -> Optional[List[Dict]]:
        """
        Get monthly follower growth with comparison to previous month
        Uses LAG window function and date functions
        """
        query = """
        WITH MonthlyFollows AS (
            SELECT 
                DATE_FORMAT(follow_date, '%Y-%m') AS follow_month,
                COUNT(listener_id) AS new_follows
            FROM follow_artist
            WHERE artist_id = %s
            GROUP BY DATE_FORMAT(follow_date, '%Y-%m')
        )
        SELECT 
            follow_month,
            new_follows,
            LAG(new_follows, 1, 0) OVER (ORDER BY follow_month) AS previous_month_follows,
            new_follows - LAG(new_follows, 1, 0) OVER (ORDER BY follow_month) AS follow_change,
            CASE 
                WHEN LAG(new_follows, 1, 0) OVER (ORDER BY follow_month) > 0 THEN
                    ROUND((new_follows - LAG(new_follows, 1, 0) OVER (ORDER BY follow_month)) * 100.0 / 
                          LAG(new_follows, 1, 0) OVER (ORDER BY follow_month), 2)
                ELSE NULL
            END AS growth_percentage
        FROM MonthlyFollows
        ORDER BY follow_month DESC
        """
        return self.db.execute_query(query, (artist_id,))

    def get_artist_recent_release_count(self, artist_id: int, days: int = 30) -> Optional[int]:
        """
        Count songs released by the artist in the last `days` days.
        """
        query = """
        SELECT COUNT(DISTINCT s.song_id) AS recent_releases
        FROM song s
        JOIN song_artist sa ON s.song_id = sa.song_id
        WHERE sa.artist_id = %s
          AND s.release_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        """
        result = self.db.execute_query(query, (artist_id, days))
        try:
            return int(result[0]['recent_releases']) if result else 0
        except Exception:
            return 0
    
    # ==================== LISTENER QUERIES ====================
    
    def get_new_songs(self, limit: int = 20, days: int = 30) -> Optional[List[Dict]]:
        """
        Get newly released songs
        Uses date functions and subqueries
        """
        query = """
        SELECT 
            s.song_id,
            s.song_name,
            s.release_date,
            s.genre,
            s.duration,
            GROUP_CONCAT(DISTINCT CONCAT(a.artist_first_name, ' ', a.artist_last_name) SEPARATOR ', ') AS artists,
            COUNT(DISTINCT si.listener_id) AS listener_count,
            COUNT(si.interaction_id) AS interaction_count
        FROM song s
        JOIN song_artist sa ON s.song_id = sa.song_id
        JOIN artist a ON sa.artist_id = a.artist_id
        LEFT JOIN song_interaction si ON s.song_id = si.song_id
        WHERE s.release_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        GROUP BY s.song_id, s.song_name, s.release_date, s.genre, s.duration
        ORDER BY s.release_date DESC, interaction_count DESC
        LIMIT %s
        """
        return self.db.execute_query(query, (days, limit))
    
    def get_followed_artists_songs(self, listener_id: int, limit: int = 20) -> Optional[List[Dict]]:
        """
        Get songs from artists the listener follows
        Uses set membership (IN subquery)
        """
        query = """
        SELECT 
            s.song_id,
            s.song_name,
            s.release_date,
            s.genre,
            CONCAT(a.artist_first_name, ' ', a.artist_last_name) AS artist_name,
            a.artist_id,
            COUNT(si.interaction_id) AS total_interactions
        FROM song s
        JOIN song_artist sa ON s.song_id = sa.song_id
        JOIN artist a ON sa.artist_id = a.artist_id
        LEFT JOIN song_interaction si ON s.song_id = si.song_id
        WHERE sa.artist_id IN (
            SELECT artist_id 
            FROM follow_artist 
            WHERE listener_id = %s
        )
        GROUP BY s.song_id, s.song_name, s.release_date, s.genre, a.artist_id, 
                 a.artist_first_name, a.artist_last_name
        ORDER BY s.release_date DESC, total_interactions DESC
        LIMIT %s
        """
        return self.db.execute_query(query, (listener_id, limit))
    
    def get_listener_recommendations(self, listener_id: int, limit: int = 10) -> Optional[List[Dict]]:
        """
        Get song recommendations based on listener's favorite genre
        New simpler logic: return songs from any genre the listener has liked.
        If the listener hasn't liked any songs (no liked genres), the caller
        can fall back to global popular songs.
        """
        query = """
        WITH LikedGenres AS (
            SELECT DISTINCT s.genre
            FROM song_interaction si
            JOIN song s ON si.song_id = s.song_id
            WHERE si.listener_id = %s
              AND si.interaction_type = 'Like'
              AND s.genre IS NOT NULL
        )
        SELECT 
            s.song_id,
            s.song_name,
            s.genre,
            s.release_date,
            GROUP_CONCAT(DISTINCT CONCAT(a.artist_first_name, ' ', a.artist_last_name) SEPARATOR ', ') AS artists,
            COUNT(DISTINCT si.listener_id) AS popularity_count
        FROM song s
        JOIN song_artist sa ON s.song_id = sa.song_id
        JOIN artist a ON sa.artist_id = a.artist_id
        LEFT JOIN song_interaction si ON s.song_id = si.song_id
        WHERE s.genre IN (SELECT genre FROM LikedGenres)
        GROUP BY s.song_id, s.song_name, s.genre, s.release_date
        ORDER BY s.release_date DESC, popularity_count DESC
        LIMIT %s
        """
        return self.db.execute_query(query, (listener_id, limit))

    def get_global_top_songs(self, limit: int = 10) -> Optional[List[Dict]]:
        """
        Get globally top performing songs by popularity (interactions).
        Used as a fallback when personalized recommendations are not available.
        """
        query = """
        SELECT
            s.song_id,
            s.song_name,
            s.genre,
            s.release_date,
            GROUP_CONCAT(DISTINCT CONCAT(a.artist_first_name, ' ', a.artist_last_name) SEPARATOR ', ') AS artists,
            COUNT(DISTINCT si.listener_id) AS popularity_count,
            COUNT(si.interaction_id) AS interaction_count
        FROM song s
        JOIN song_artist sa ON s.song_id = sa.song_id
        JOIN artist a ON sa.artist_id = a.artist_id
        LEFT JOIN song_interaction si ON s.song_id = si.song_id
        GROUP BY s.song_id, s.song_name, s.genre, s.release_date
        ORDER BY popularity_count DESC, interaction_count DESC, s.release_date DESC
        LIMIT %s
        """
        return self.db.execute_query(query, (limit,))
    
    def get_listener_statistics(self, listener_id: int) -> Optional[Dict]:
        """Get listener's listening statistics"""
        query = """
        SELECT 
            COUNT(DISTINCT si.song_id) AS unique_songs_played,
            COUNT(si.interaction_id) AS total_interactions,
            COUNT(CASE WHEN si.interaction_type = 'Play' THEN 1 END) AS total_plays,
            COUNT(CASE WHEN si.interaction_type = 'Like' THEN 1 END) AS total_likes,
            COUNT(CASE WHEN si.interaction_type = 'Share' THEN 1 END) AS total_shares,
            COUNT(DISTINCT sa.artist_id) AS unique_artists_listened,
            COUNT(DISTINCT fa.artist_id) AS artists_followed,
            COUNT(DISTINCT s.genre) AS genres_explored
        FROM listener l
        LEFT JOIN song_interaction si ON l.listener_id = si.listener_id
        LEFT JOIN song s ON si.song_id = s.song_id
        LEFT JOIN song_artist sa ON s.song_id = sa.song_id
        LEFT JOIN follow_artist fa ON l.listener_id = fa.listener_id
        WHERE l.listener_id = %s
        """
        result = self.db.execute_query(query, (listener_id,))
        return result[0] if result else None
    
    # ==================== OLAP QUERIES ====================
    
    def get_interactions_by_account_type_and_genre(self) -> Optional[List[Dict]]:
        """
        OLAP query using ROLLUP to get interactions by account type and genre
        """
        query = """
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
        """
        return self.db.execute_query(query)
    
    def get_artist_performance_by_country_and_genre(self, artist_id: int) -> Optional[List[Dict]]:
        """
        OLAP query using CUBE-like operations for multi-dimensional analysis
        """
        query = """
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
        """
        return self.db.execute_query(query, (artist_id,))
    
    # ==================== SET OPERATIONS ====================
    
    def get_artists_with_no_interactions(self) -> Optional[List[Dict]]:
        """
        Find artists who have songs but no interactions
        Uses set difference (NOT EXISTS)
        """
        query = """
        SELECT 
            a.artist_id,
            CONCAT(a.artist_first_name, ' ', a.artist_last_name) AS artist_name,
            COUNT(DISTINCT sa.song_id) AS total_songs
        FROM artist a
        JOIN song_artist sa ON a.artist_id = sa.artist_id
        WHERE NOT EXISTS (
            SELECT 1
            FROM song_interaction si
            WHERE si.song_id = sa.song_id
        )
        GROUP BY a.artist_id, a.artist_first_name, a.artist_last_name
        ORDER BY total_songs DESC
        """
        return self.db.execute_query(query)
    
    def get_listeners_who_follow_but_never_interact(self, artist_id: int) -> Optional[List[Dict]]:
        """
        Find listeners who follow an artist but never interacted with their songs
        Uses set difference
        """
        query = """
        SELECT 
            l.listener_id,
            CONCAT(l.listener_first_name, ' ', l.listener_last_name) AS listener_name,
            l.email,
            fa.follow_date
        FROM listener l
        JOIN follow_artist fa ON l.listener_id = fa.listener_id
        WHERE fa.artist_id = %s
          AND l.listener_id NOT IN (
              SELECT DISTINCT si.listener_id
              FROM song_interaction si
              JOIN song_artist sa ON si.song_id = sa.song_id
              WHERE sa.artist_id = %s
          )
        ORDER BY fa.follow_date DESC
        """
        return self.db.execute_query(query, (artist_id, artist_id))

