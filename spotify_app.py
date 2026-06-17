#!/usr/bin/env python3
"""
Spotify Application - Main Entry Point
Integrated application with Artist Dashboard and Listener Interface
"""

from db_connection import DatabaseConnection
from auth import Authentication
from artist_dashboard import ArtistDashboard
from listener_interface import ListenerInterface


class SpotifyApp:
    """Main application class"""
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.auth = None
        self.current_user = None
    
    def connect(self):
        """Connect to database"""
        if self.db.connect():
            self.auth = Authentication(self.db)
            print("✓ Connected to Spotify database successfully!")
            return True
        else:
            print("✗ Failed to connect to database")
            return False
    
    def disconnect(self):
        """Disconnect from database"""
        self.db.disconnect()
    
    def print_welcome(self):
        """Print welcome screen"""
        print("\n" + "="*80)
        print("  SPOTIFY DATABASE APPLICATION")
        print("  Artist Dashboard & Listener Interface")
        print("="*80)
    
    def print_login_menu(self):
        """Print login menu"""
        print("\nLogin Options:")
        print("  1. Login as Artist")
        print("  2. Login as Listener")
        print("  3. Exit")
        print("="*80)
    
    def login_artist(self):
        """Login as artist"""
        print("\n" + "-"*80)
        print("  ARTIST LOGIN")
        print("-"*80)
        
        # Show available artists
        artists = self.auth.list_artists()
        if artists:
            print("\nAvailable Artists:")
            for artist in artists[:20]:  # Show first 20
                print(f"  ID: {artist['artist_id']:3d} - {artist['artist_first_name']} {artist['artist_last_name']} "
                      f"({artist['country'] or 'N/A'}, {artist['genre'] or 'N/A'})")
        
        try:
            artist_id = int(input("\nEnter Artist ID to login: ").strip())
            user = self.auth.login_artist(artist_id)
            if user:
                self.current_user = user
                print(f"\n✓ Logged in as {user['artist_first_name']} {user['artist_last_name']}")
                return True
            else:
                print("✗ Artist not found")
                return False
        except ValueError:
            print("✗ Invalid Artist ID")
            return False
    
    def login_listener(self):
        """Login as listener"""
        print("\n" + "-"*80)
        print("  LISTENER LOGIN")
        print("-"*80)
        
        print("\nLogin Options:")
        print("  1. Login by Email")
        print("  2. Login by ID")
        
        choice = input("Enter choice: ").strip()
        
        if choice == '1':
            email = input("Enter Email: ").strip()
            user = self.auth.login_listener(email=email)
        elif choice == '2':
            try:
                listener_id = int(input("Enter Listener ID: ").strip())
                user = self.auth.login_listener(listener_id=listener_id)
            except ValueError:
                print("✗ Invalid Listener ID")
                return False
        else:
            print("✗ Invalid choice")
            return False
        
        if user:
            self.current_user = user
            print(f"\n✓ Logged in as {user['listener_first_name']} {user['listener_last_name']}")
            return True
        else:
            print("✗ Listener not found")
            return False
    
    def run(self):
        """Main run loop"""
        if not self.connect():
            return
        
        try:
            while True:
                self.print_welcome()
                self.print_login_menu()
                choice = input("\nEnter your choice: ").strip()
                
                if choice == '1':
                    if self.login_artist():
                        # Launch Artist Dashboard
                        dashboard = ArtistDashboard(self.db, self.current_user['artist_id'])
                        dashboard.run()
                        self.current_user = None
                
                elif choice == '2':
                    if self.login_listener():
                        # Launch Listener Interface
                        interface = ListenerInterface(self.db, self.current_user['listener_id'])
                        interface.run()
                        self.current_user = None
                
                elif choice == '3':
                    print("\nThank you for using Spotify Application!")
                    break
                else:
                    print("Invalid choice. Please try again.")
        
        except KeyboardInterrupt:
            print("\n\nExiting...")
        finally:
            self.disconnect()


def main():
    """Main entry point"""
    app = SpotifyApp()
    app.run()


if __name__ == "__main__":
    main()

