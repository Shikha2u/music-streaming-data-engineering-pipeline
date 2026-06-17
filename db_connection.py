"""
Database Connection Module for Spotify Database
Handles MySQL database connections and connection management
"""

import mysql.connector
from mysql.connector import Error
from mysql.connector import pooling
from typing import Optional


class DatabaseConnection:
    """Manages database connections using a connection pool.

    Avoids sharing a single MySQLConnection object across threads. Each
    query acquires a connection from the pool and returns it when done.
    This prevents C-extension crashes when the server (Waitress/Gunicorn)
    uses threads.
    """

    def __init__(self, host='localhost', user='root', password='', database='spotify_db', pool_size: int = 5):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.pool_size = pool_size
        self.pool: Optional[pooling.MySQLConnectionPool] = None

    def connect(self) -> bool:
        """Create a connection pool and verify connectivity."""
        try:
            if self.pool is None:
                self.pool = pooling.MySQLConnectionPool(
                    pool_name="spotify_pool",
                    pool_size=self.pool_size,
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )

            # verify by getting and releasing a connection
            conn = self.pool.get_connection()
            connected = conn.is_connected()
            conn.close()
            return bool(connected)
        except Error as e:
            print(f"Error creating MySQL connection pool: {e}")
            return False

    def disconnect(self):
        """Close the pool (no direct API to close pool connections; clear ref)."""
        # MySQLConnectionPool doesn't implement an explicit close; setting
        # pool to None allows connections to be garbage-collected on shutdown.
        self.pool = None

    def get_connection(self) -> Optional[mysql.connector.connection.MySQLConnection]:
        """Acquire a connection from the pool, creating the pool if needed."""
        if self.pool is None:
            if not self.connect():
                return None
        try:
            return self.pool.get_connection()
        except Error as e:
            print(f"Error getting pooled connection: {e}")
            return None

    def execute_query(self, query: str, params: tuple = None) -> Optional[list]:
        """Execute a SELECT query and return results. Uses a pooled connection."""
        conn = self.get_connection()
        if conn is None:
            return None
        try:
            cursor = conn.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            return result
        except Error as e:
            # ensure connection is closed on error
            try:
                conn.close()
            except Exception:
                pass
            print(f"Error executing query: {e}")
            return None

    def execute_update(self, query: str, params: tuple = None) -> bool:
        """Execute an INSERT/UPDATE/DELETE using a pooled connection."""
        conn = self.get_connection()
        if conn is None:
            return False
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Error as e:
            try:
                conn.rollback()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass
            print(f"Error executing update: {e}")
            return False

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()

