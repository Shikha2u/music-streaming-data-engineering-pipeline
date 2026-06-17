"""
CRUD Operations Module for Spotify Database
Implements Create, Read, Update, Delete operations for all entities
"""

from db_connection import DatabaseConnection
from datetime import datetime
from typing import Optional, List, Dict


class ArtistCRUD:
    """CRUD operations for Artist entity"""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
    
    def create(self, first_name: str, last_name: str, country: str = None, 
               bio: str = None, genre: str = None, join_date: str = None) -> bool:
        """Create a new artist"""
        query = """
        INSERT INTO artist (artist_first_name, artist_last_name, country, bio, genre, join_date)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (first_name, last_name, country, bio, genre, join_date)
        return self.db.execute_update(query, params)
    
    def read_all(self) -> Optional[List[Dict]]:
        """Read all artists"""
        query = "SELECT * FROM artist ORDER BY artist_id"
        return self.db.execute_query(query)
    
    def read_by_id(self, artist_id: int) -> Optional[Dict]:
        """Read artist by ID"""
        query = "SELECT * FROM artist WHERE artist_id = %s"
        result = self.db.execute_query(query, (artist_id,))
        return result[0] if result else None
    
    def read_by_name(self, first_name: str, last_name: str) -> Optional[List[Dict]]:
        """Read artists by name"""
        query = """
        SELECT * FROM artist 
        WHERE artist_first_name LIKE %s AND artist_last_name LIKE %s
        """
        params = (f"%{first_name}%", f"%{last_name}%")
        return self.db.execute_query(query, params)
    
    def update(self, artist_id: int, first_name: str = None, last_name: str = None,
               country: str = None, bio: str = None, genre: str = None, 
               join_date: str = None) -> bool:
        """Update artist information"""
        updates = []
        params = []
        
        if first_name:
            updates.append("artist_first_name = %s")
            params.append(first_name)
        if last_name:
            updates.append("artist_last_name = %s")
            params.append(last_name)
        if country:
            updates.append("country = %s")
            params.append(country)
        if bio:
            updates.append("bio = %s")
            params.append(bio)
        if genre:
            updates.append("genre = %s")
            params.append(genre)
        if join_date:
            updates.append("join_date = %s")
            params.append(join_date)
        
        if not updates:
            return False
        
        params.append(artist_id)
        query = f"UPDATE artist SET {', '.join(updates)} WHERE artist_id = %s"
        return self.db.execute_update(query, tuple(params))
    
    def delete(self, artist_id: int) -> bool:
        """Delete an artist"""
        query = "DELETE FROM artist WHERE artist_id = %s"
        return self.db.execute_update(query, (artist_id,))


class SongCRUD:
    """CRUD operations for Song entity"""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
    
    def create(self, song_name: str, title: str = None, duration: int = None,
               genre: str = None, release_date: str = None) -> Optional[int]:
        """Create a new song and return song_id"""
        query = """
        INSERT INTO song (song_name, title, duration, genre, release_date)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (song_name, title, duration, genre, release_date)
        # Use a single connection for insert + LAST_INSERT_ID() because
        # LAST_INSERT_ID() is connection-scoped. With a pooled connection
        # implementation we must use the same connection for both calls.
        conn = self.db.get_connection()
        if conn is None:
            return None
        try:
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            cur.execute("SELECT LAST_INSERT_ID() as id")
            row = cur.fetchone()
            # Support both tuple and dict cursor results
            try:
                last_id = row[0] if row else None
            except Exception:
                last_id = row.get('id') if isinstance(row, dict) else None
            cur.close()
            conn.close()
            return int(last_id) if last_id else None
        except Exception:
            try:
                conn.close()
            except Exception:
                pass
            return None
    
    def read_all(self) -> Optional[List[Dict]]:
        """Read all songs"""
        query = "SELECT * FROM song ORDER BY song_id"
        return self.db.execute_query(query)
    
    def read_by_id(self, song_id: int) -> Optional[Dict]:
        """Read song by ID"""
        query = "SELECT * FROM song WHERE song_id = %s"
        result = self.db.execute_query(query, (song_id,))
        return result[0] if result else None
    
    def read_by_name(self, song_name: str) -> Optional[List[Dict]]:
        """Read songs by name"""
        query = "SELECT * FROM song WHERE song_name LIKE %s"
        return self.db.execute_query(query, (f"%{song_name}%",))
    
    def update(self, song_id: int, song_name: str = None, title: str = None,
               duration: int = None, genre: str = None, release_date: str = None) -> bool:
        """Update song information"""
        updates = []
        params = []
        
        if song_name:
            updates.append("song_name = %s")
            params.append(song_name)
        if title:
            updates.append("title = %s")
            params.append(title)
        if duration:
            updates.append("duration = %s")
            params.append(duration)
        if genre:
            updates.append("genre = %s")
            params.append(genre)
        if release_date:
            updates.append("release_date = %s")
            params.append(release_date)
        
        if not updates:
            return False
        
        params.append(song_id)
        query = f"UPDATE song SET {', '.join(updates)} WHERE song_id = %s"
        return self.db.execute_update(query, tuple(params))
    
    def delete(self, song_id: int) -> bool:
        """Delete a song"""
        query = "DELETE FROM song WHERE song_id = %s"
        return self.db.execute_update(query, (song_id,))
    
    def link_artist(self, song_id: int, artist_id: int) -> bool:
        """Link a song to an artist"""
        query = """
        INSERT INTO song_artist (song_id, artist_id)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE song_id = song_id
        """
        return self.db.execute_update(query, (song_id, artist_id))


class ListenerCRUD:
    """CRUD operations for Listener entity"""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
    
    def create(self, first_name: str, last_name: str, date_of_birth: str,
               gender: str, email: str, country: str = None, 
               join_date: str = None, account_id: int = None) -> bool:
        """Create a new listener"""
        if not account_id:
            # Create a default Free account
            account_query = "INSERT INTO listener_account_type (account_type, start_date, auto_renew) VALUES ('Free', CURDATE(), FALSE)"
            # perform insert and fetch last id on the same connection
            conn = self.db.get_connection()
            if conn is None:
                return False
            try:
                cur = conn.cursor()
                cur.execute(account_query)
                conn.commit()
                cur.execute("SELECT LAST_INSERT_ID() as id")
                row = cur.fetchone()
                try:
                    account_id = row[0] if row else None
                except Exception:
                    account_id = row.get('id') if isinstance(row, dict) else None
                cur.close()
                conn.close()
            except Exception:
                try:
                    conn.close()
                except Exception:
                    pass
                return False
        
        query = """
        INSERT INTO listener (listener_first_name, listener_last_name, Date_of_birth, 
                            gender, email, country, join_date, account_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (first_name, last_name, date_of_birth, gender, email, 
                 country, join_date, account_id)
        return self.db.execute_update(query, params)
    
    def read_all(self) -> Optional[List[Dict]]:
        """Read all listeners"""
        query = "SELECT * FROM listener ORDER BY listener_id"
        return self.db.execute_query(query)
    
    def read_by_id(self, listener_id: int) -> Optional[Dict]:
        """Read listener by ID"""
        query = "SELECT * FROM listener WHERE listener_id = %s"
        result = self.db.execute_query(query, (listener_id,))
        return result[0] if result else None
    
    def read_by_email(self, email: str) -> Optional[Dict]:
        """Read listener by email"""
        query = "SELECT * FROM listener WHERE email = %s"
        result = self.db.execute_query(query, (email,))
        return result[0] if result else None
    
    def update(self, listener_id: int, first_name: str = None, last_name: str = None,
               date_of_birth: str = None, gender: str = None, email: str = None,
               country: str = None, account_id: int = None) -> bool:
        """Update listener information"""
        updates = []
        params = []
        
        if first_name:
            updates.append("listener_first_name = %s")
            params.append(first_name)
        if last_name:
            updates.append("listener_last_name = %s")
            params.append(last_name)
        if date_of_birth:
            updates.append("Date_of_birth = %s")
            params.append(date_of_birth)
        if gender:
            updates.append("gender = %s")
            params.append(gender)
        if email:
            updates.append("email = %s")
            params.append(email)
        if country:
            updates.append("country = %s")
            params.append(country)
        if account_id:
            updates.append("account_id = %s")
            params.append(account_id)
        
        if not updates:
            return False
        
        params.append(listener_id)
        query = f"UPDATE listener SET {', '.join(updates)} WHERE listener_id = %s"
        return self.db.execute_update(query, tuple(params))
    
    def delete(self, listener_id: int) -> bool:
        """Delete a listener"""
        query = "DELETE FROM listener WHERE listener_id = %s"
        return self.db.execute_update(query, (listener_id,))


class SongInteractionCRUD:
    """CRUD operations for Song Interaction entity"""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
    
    def create(self, listener_id: int, song_id: int, interaction_type: str,
               interaction_timestamp: str = None) -> bool:
        """Create a new song interaction"""
        if not interaction_timestamp:
            interaction_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        query = """
        INSERT INTO song_interaction (listener_id, song_id, interaction_type, interaction_timestamp)
        VALUES (%s, %s, %s, %s)
        """
        params = (listener_id, song_id, interaction_type, interaction_timestamp)
        return self.db.execute_update(query, params)
    
    def read_all(self) -> Optional[List[Dict]]:
        """Read all interactions"""
        query = """
        SELECT si.*, s.song_name, l.listener_first_name, l.listener_last_name
        FROM song_interaction si
        JOIN song s ON si.song_id = s.song_id
        JOIN listener l ON si.listener_id = l.listener_id
        ORDER BY si.interaction_timestamp DESC
        """
        return self.db.execute_query(query)
    
    def read_by_id(self, interaction_id: int) -> Optional[Dict]:
        """Read interaction by ID"""
        query = """
        SELECT si.*, s.song_name, l.listener_first_name, l.listener_last_name
        FROM song_interaction si
        JOIN song s ON si.song_id = s.song_id
        JOIN listener l ON si.listener_id = l.listener_id
        WHERE si.interaction_id = %s
        """
        result = self.db.execute_query(query, (interaction_id,))
        return result[0] if result else None
    
    def read_by_listener(self, listener_id: int) -> Optional[List[Dict]]:
        """Read all interactions by a listener"""
        query = """
        SELECT si.*, s.song_name
        FROM song_interaction si
        JOIN song s ON si.song_id = s.song_id
        WHERE si.listener_id = %s
        ORDER BY si.interaction_timestamp DESC
        """
        return self.db.execute_query(query, (listener_id,))
    
    def read_by_song(self, song_id: int) -> Optional[List[Dict]]:
        """Read all interactions for a song"""
        query = """
        SELECT si.*, l.listener_first_name, l.listener_last_name
        FROM song_interaction si
        JOIN listener l ON si.listener_id = l.listener_id
        WHERE si.song_id = %s
        ORDER BY si.interaction_timestamp DESC
        """
        return self.db.execute_query(query, (song_id,))
    
    def update(self, interaction_id: int, interaction_type: str = None,
               interaction_timestamp: str = None) -> bool:
        """Update interaction information"""
        updates = []
        params = []
        
        if interaction_type:
            updates.append("interaction_type = %s")
            params.append(interaction_type)
        if interaction_timestamp:
            updates.append("interaction_timestamp = %s")
            params.append(interaction_timestamp)
        
        if not updates:
            return False
        
        params.append(interaction_id)
        query = f"UPDATE song_interaction SET {', '.join(updates)} WHERE interaction_id = %s"
        return self.db.execute_update(query, tuple(params))
    
    def delete(self, interaction_id: int) -> bool:
        """Delete an interaction"""
        query = "DELETE FROM song_interaction WHERE interaction_id = %s"
        return self.db.execute_update(query, (interaction_id,))


class FollowArtistCRUD:
    """CRUD operations for Follow Artist entity"""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
    
    def create(self, listener_id: int, artist_id: int, follow_date: str = None) -> bool:
        """Create a new follow relationship"""
        if not follow_date:
            follow_date = datetime.now().strftime('%Y-%m-%d')
        
        query = """
        INSERT INTO follow_artist (listener_id, artist_id, follow_date)
        VALUES (%s, %s, %s)
        """
        params = (listener_id, artist_id, follow_date)
        return self.db.execute_update(query, params)
    
    def read_all(self) -> Optional[List[Dict]]:
        """Read all follow relationships"""
        query = """
        SELECT fa.*, a.artist_first_name, a.artist_last_name, 
               l.listener_first_name, l.listener_last_name
        FROM follow_artist fa
        JOIN artist a ON fa.artist_id = a.artist_id
        JOIN listener l ON fa.listener_id = l.listener_id
        ORDER BY fa.follow_date DESC
        """
        return self.db.execute_query(query)
    
    def read_by_listener(self, listener_id: int) -> Optional[List[Dict]]:
        """Read all artists followed by a listener"""
        query = """
        SELECT fa.*, a.artist_first_name, a.artist_last_name
        FROM follow_artist fa
        JOIN artist a ON fa.artist_id = a.artist_id
        WHERE fa.listener_id = %s
        ORDER BY fa.follow_date DESC
        """
        return self.db.execute_query(query, (listener_id,))
    
    def read_by_artist(self, artist_id: int) -> Optional[List[Dict]]:
        """Read all listeners following an artist"""
        query = """
        SELECT fa.*, l.listener_first_name, l.listener_last_name
        FROM follow_artist fa
        JOIN listener l ON fa.listener_id = l.listener_id
        WHERE fa.artist_id = %s
        ORDER BY fa.follow_date DESC
        """
        return self.db.execute_query(query, (artist_id,))
    
    def delete(self, listener_id: int, artist_id: int) -> bool:
        """Delete a follow relationship"""
        query = "DELETE FROM follow_artist WHERE listener_id = %s AND artist_id = %s"
        return self.db.execute_update(query, (listener_id, artist_id))


class ListenerAccountTypeCRUD:
    """CRUD operations for Listener Account Type entity"""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
    
    def create(self, account_type: str, start_date: str = None, 
               end_date: str = None, auto_renew: bool = False) -> Optional[int]:
        """Create a new account type and return account_id"""
        query = """
        INSERT INTO listener_account_type (account_type, start_date, end_date, auto_renew)
        VALUES (%s, %s, %s, %s)
        """
        params = (account_type, start_date, end_date, auto_renew)
        # Use single connection to get LAST_INSERT_ID()
        conn = self.db.get_connection()
        if conn is None:
            return None
        try:
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            cur.execute("SELECT LAST_INSERT_ID() as id")
            row = cur.fetchone()
            try:
                last_id = row[0] if row else None
            except Exception:
                last_id = row.get('id') if isinstance(row, dict) else None
            cur.close()
            conn.close()
            return int(last_id) if last_id else None
        except Exception:
            try:
                conn.close()
            except Exception:
                pass
            return None
    
    def read_all(self) -> Optional[List[Dict]]:
        """Read all account types"""
        query = "SELECT * FROM listener_account_type ORDER BY account_id"
        return self.db.execute_query(query)
    
    def read_by_id(self, account_id: int) -> Optional[Dict]:
        """Read account type by ID"""
        query = "SELECT * FROM listener_account_type WHERE account_id = %s"
        result = self.db.execute_query(query, (account_id,))
        return result[0] if result else None
    
    def read_by_type(self, account_type: str) -> Optional[List[Dict]]:
        """Read account types by type"""
        query = "SELECT * FROM listener_account_type WHERE account_type = %s"
        return self.db.execute_query(query, (account_type,))
    
    def update(self, account_id: int, account_type: str = None, 
               start_date: str = None, end_date: str = None, 
               auto_renew: bool = None) -> bool:
        """Update account type information"""
        updates = []
        params = []
        
        if account_type:
            updates.append("account_type = %s")
            params.append(account_type)
        if start_date:
            updates.append("start_date = %s")
            params.append(start_date)
        if end_date:
            updates.append("end_date = %s")
            params.append(end_date)
        if auto_renew is not None:
            updates.append("auto_renew = %s")
            params.append(auto_renew)
        
        if not updates:
            return False
        
        params.append(account_id)
        query = f"UPDATE listener_account_type SET {', '.join(updates)} WHERE account_id = %s"
        return self.db.execute_update(query, tuple(params))
    
    def delete(self, account_id: int) -> bool:
        """Delete an account type"""
        query = "DELETE FROM listener_account_type WHERE account_id = %s"
        return self.db.execute_update(query, (account_id,))


class SongArtistCRUD:
    """CRUD operations for Song-Artist junction table"""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
    
    def create(self, song_id: int, artist_id: int) -> bool:
        """Create a song-artist relationship"""
        query = """
        INSERT INTO song_artist (song_id, artist_id)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE song_id = song_id
        """
        return self.db.execute_update(query, (song_id, artist_id))
    
    def read_all(self) -> Optional[List[Dict]]:
        """Read all song-artist relationships"""
        query = """
        SELECT sa.*, s.song_name, a.artist_first_name, a.artist_last_name
        FROM song_artist sa
        JOIN song s ON sa.song_id = s.song_id
        JOIN artist a ON sa.artist_id = a.artist_id
        ORDER BY sa.song_id, sa.artist_id
        """
        return self.db.execute_query(query)
    
    def read_by_song(self, song_id: int) -> Optional[List[Dict]]:
        """Read all artists for a song"""
        query = """
        SELECT sa.*, a.artist_first_name, a.artist_last_name
        FROM song_artist sa
        JOIN artist a ON sa.artist_id = a.artist_id
        WHERE sa.song_id = %s
        """
        return self.db.execute_query(query, (song_id,))
    
    def read_by_artist(self, artist_id: int) -> Optional[List[Dict]]:
        """Read all songs for an artist"""
        query = """
        SELECT sa.*, s.song_name
        FROM song_artist sa
        JOIN song s ON sa.song_id = s.song_id
        WHERE sa.artist_id = %s
        """
        return self.db.execute_query(query, (artist_id,))
    
    def delete(self, song_id: int, artist_id: int) -> bool:
        """Delete a song-artist relationship"""
        query = "DELETE FROM song_artist WHERE song_id = %s AND artist_id = %s"
        return self.db.execute_update(query, (song_id, artist_id))

