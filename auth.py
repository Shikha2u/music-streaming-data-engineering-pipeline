"""
Authentication Module for Spotify Database
Handles user login and role-based access
"""

from db_connection import DatabaseConnection
from typing import Optional, Dict, Tuple


class Authentication:
    """Handles user authentication for Artists and Listeners"""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
    
    def login_artist(self, artist_id: int) -> Optional[Dict]:
        """Login as an artist by ID"""
        query = """
        SELECT artist_id, artist_first_name, artist_last_name, country, genre,
               bio, join_date
        FROM artist
        WHERE artist_id = %s
        """
        result = self.db.execute_query(query, (artist_id,))
        if result:
            artist = result[0]
            artist['role'] = 'artist'
            return artist
        return None
    
    def login_listener(self, listener_id: int = None, email: str = None) -> Optional[Dict]:
        """Login as a listener by ID or email"""
        if email:
            query = """
            SELECT listener_id, listener_first_name, listener_last_name, email, country
            FROM listener
            WHERE email = %s
            """
            result = self.db.execute_query(query, (email,))
        elif listener_id:
            query = """
            SELECT listener_id, listener_first_name, listener_last_name, email, country
            FROM listener
            WHERE listener_id = %s
            """
            result = self.db.execute_query(query, (listener_id,))
        else:
            return None
        
        if result:
            listener = result[0]
            listener['role'] = 'listener'
            return listener
        return None
    
    def list_artists(self) -> list:
        """List all artists for selection"""
        query = """
        SELECT artist_id, artist_first_name, artist_last_name, country, genre
        FROM artist
        ORDER BY artist_first_name, artist_last_name
        """
        return self.db.execute_query(query) or []
    
    def list_listeners(self, limit: int = 20) -> list:
        """List listeners for selection"""
        query = """
        SELECT listener_id, listener_first_name, listener_last_name, email
        FROM listener
        ORDER BY listener_id
        LIMIT %s
        """
        return self.db.execute_query(query, (limit,)) or []

