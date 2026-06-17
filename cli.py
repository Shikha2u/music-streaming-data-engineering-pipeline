#!/usr/bin/env python3
"""
Command-Line Interface for Spotify Database CRUD Operations
Main entry point for the CLI application
"""

import sys
from db_connection import DatabaseConnection
from crud_operations import (
    ArtistCRUD, SongCRUD, ListenerCRUD, 
    SongInteractionCRUD, FollowArtistCRUD,
    ListenerAccountTypeCRUD, SongArtistCRUD
)


class SpotifyCLI:
    """Main CLI interface for Spotify database operations"""
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.artist_crud = None
        self.song_crud = None
        self.listener_crud = None
        self.interaction_crud = None
        self.follow_crud = None
        self.account_type_crud = None
        self.song_artist_crud = None
    
    def connect(self):
        """Connect to database and initialize CRUD operations"""
        if self.db.connect():
            self.artist_crud = ArtistCRUD(self.db)
            self.song_crud = SongCRUD(self.db)
            self.listener_crud = ListenerCRUD(self.db)
            self.interaction_crud = SongInteractionCRUD(self.db)
            self.follow_crud = FollowArtistCRUD(self.db)
            self.account_type_crud = ListenerAccountTypeCRUD(self.db)
            self.song_artist_crud = SongArtistCRUD(self.db)
            print("✓ Connected to Spotify database successfully!")
            return True
        else:
            print("✗ Failed to connect to database")
            return False
    
    def disconnect(self):
        """Disconnect from database"""
        self.db.disconnect()
    
    def print_menu(self):
        """Print main menu"""
        print("\n" + "="*60)
        print("  SPOTIFY DATABASE MANAGEMENT SYSTEM")
        print("="*60)
        print("\nMain Menu:")
        print("  1. Artist Operations")
        print("  2. Song Operations")
        print("  3. Listener Operations")
        print("  4. Song Interaction Operations")
        print("  5. Follow Artist Operations")
        print("  6. Account Type Operations")
        print("  7. Song-Artist Relationship Operations")
        print("  8. Exit")
        print("="*60)
    
    def print_artist_menu(self):
        """Print artist operations menu"""
        print("\n" + "-"*60)
        print("  ARTIST OPERATIONS")
        print("-"*60)
        print("  1. Create Artist")
        print("  2. Read All Artists")
        print("  3. Read Artist by ID")
        print("  4. Read Artist by Name")
        print("  5. Update Artist")
        print("  6. Delete Artist")
        print("  7. Back to Main Menu")
        print("-"*60)
    
    def print_song_menu(self):
        """Print song operations menu"""
        print("\n" + "-"*60)
        print("  SONG OPERATIONS")
        print("-"*60)
        print("  1. Create Song")
        print("  2. Read All Songs")
        print("  3. Read Song by ID")
        print("  4. Read Song by Name")
        print("  5. Update Song")
        print("  6. Delete Song")
        print("  7. Link Song to Artist")
        print("  8. Back to Main Menu")
        print("-"*60)
    
    def print_listener_menu(self):
        """Print listener operations menu"""
        print("\n" + "-"*60)
        print("  LISTENER OPERATIONS")
        print("-"*60)
        print("  1. Create Listener")
        print("  2. Read All Listeners")
        print("  3. Read Listener by ID")
        print("  4. Read Listener by Email")
        print("  5. Update Listener")
        print("  6. Delete Listener")
        print("  7. Back to Main Menu")
        print("-"*60)
    
    def print_interaction_menu(self):
        """Print interaction operations menu"""
        print("\n" + "-"*60)
        print("  SONG INTERACTION OPERATIONS")
        print("-"*60)
        print("  1. Create Interaction (Play/Like/Share/Skip)")
        print("  2. Read All Interactions")
        print("  3. Read Interaction by ID")
        print("  4. Read Interactions by Listener")
        print("  5. Read Interactions by Song")
        print("  6. Update Interaction")
        print("  7. Delete Interaction")
        print("  8. Back to Main Menu")
        print("-"*60)
    
    def print_follow_menu(self):
        """Print follow operations menu"""
        print("\n" + "-"*60)
        print("  FOLLOW ARTIST OPERATIONS")
        print("-"*60)
        print("  1. Follow Artist")
        print("  2. Read All Follows")
        print("  3. Read Artists Followed by Listener")
        print("  4. Read Listeners Following Artist")
        print("  5. Unfollow Artist")
        print("  6. Back to Main Menu")
        print("-"*60)
    
    def handle_artist_operations(self):
        """Handle artist CRUD operations"""
        while True:
            self.print_artist_menu()
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':  # Create
                first_name = input("First Name: ").strip()
                last_name = input("Last Name: ").strip()
                country = input("Country (optional): ").strip() or None
                bio = input("Bio (optional): ").strip() or None
                genre = input("Genre (optional): ").strip() or None
                join_date = input("Join Date (YYYY-MM-DD, optional): ").strip() or None
                
                if self.artist_crud.create(first_name, last_name, country, bio, genre, join_date):
                    print("✓ Artist created successfully!")
                else:
                    print("✗ Failed to create artist")
            
            elif choice == '2':  # Read All
                artists = self.artist_crud.read_all()
                if artists:
                    print(f"\nFound {len(artists)} artists:")
                    print("-" * 80)
                    for a in artists:
                        print(f"ID: {a['artist_id']:3d} | {a['artist_first_name']} {a['artist_last_name']} | "
                              f"Country: {a['country'] or 'N/A':15s} | Genre: {a['genre'] or 'N/A'}")
                else:
                    print("No artists found")
            
            elif choice == '3':  # Read by ID
                try:
                    artist_id = int(input("Artist ID: ").strip())
                    artist = self.artist_crud.read_by_id(artist_id)
                    if artist:
                        self.print_dict(artist)
                    else:
                        print("Artist not found")
                except ValueError:
                    print("Invalid ID")
            
            elif choice == '4':  # Read by Name
                first_name = input("First Name (partial match): ").strip()
                last_name = input("Last Name (partial match): ").strip()
                artists = self.artist_crud.read_by_name(first_name, last_name)
                if artists:
                    print(f"\nFound {len(artists)} artists:")
                    for a in artists:
                        self.print_dict(a)
                else:
                    print("No artists found")
            
            elif choice == '5':  # Update
                try:
                    artist_id = int(input("Artist ID to update: ").strip())
                    print("Enter new values (press Enter to skip):")
                    first_name = input("First Name: ").strip() or None
                    last_name = input("Last Name: ").strip() or None
                    country = input("Country: ").strip() or None
                    bio = input("Bio: ").strip() or None
                    genre = input("Genre: ").strip() or None
                    join_date = input("Join Date (YYYY-MM-DD): ").strip() or None
                    
                    if self.artist_crud.update(artist_id, first_name, last_name, 
                                              country, bio, genre, join_date):
                        print("✓ Artist updated successfully!")
                    else:
                        print("✗ Failed to update artist")
                except ValueError:
                    print("Invalid ID")
            
            elif choice == '6':  # Delete
                try:
                    artist_id = int(input("Artist ID to delete: ").strip())
                    confirm = input(f"Are you sure you want to delete artist {artist_id}? (yes/no): ").strip().lower()
                    if confirm == 'yes':
                        if self.artist_crud.delete(artist_id):
                            print("✓ Artist deleted successfully!")
                        else:
                            print("✗ Failed to delete artist")
                    else:
                        print("Deletion cancelled")
                except ValueError:
                    print("Invalid ID")
            
            elif choice == '7':
                break
            else:
                print("Invalid choice")
    
    def handle_song_operations(self):
        """Handle song CRUD operations"""
        while True:
            self.print_song_menu()
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':  # Create
                song_name = input("Song Name: ").strip()
                title = input("Title (optional): ").strip() or None
                try:
                    duration = int(input("Duration (seconds): ").strip()) if input("Enter duration? (y/n): ").strip().lower() == 'y' else None
                except ValueError:
                    duration = None
                genre = input("Genre (optional): ").strip() or None
                release_date = input("Release Date (YYYY-MM-DD, optional): ").strip() or None
                
                song_id = self.song_crud.create(song_name, title, duration, genre, release_date)
                if song_id:
                    print(f"✓ Song created successfully! Song ID: {song_id}")
                else:
                    print("✗ Failed to create song")
            
            elif choice == '2':  # Read All
                songs = self.song_crud.read_all()
                if songs:
                    print(f"\nFound {len(songs)} songs:")
                    print("-" * 80)
                    for s in songs:
                        print(f"ID: {s['song_id']:3d} | {s['song_name']:30s} | "
                              f"Duration: {s['duration'] or 'N/A':5s}s | Genre: {s['genre'] or 'N/A'}")
                else:
                    print("No songs found")
            
            elif choice == '3':  # Read by ID
                try:
                    song_id = int(input("Song ID: ").strip())
                    song = self.song_crud.read_by_id(song_id)
                    if song:
                        self.print_dict(song)
                    else:
                        print("Song not found")
                except ValueError:
                    print("Invalid ID")
            
            elif choice == '4':  # Read by Name
                song_name = input("Song Name (partial match): ").strip()
                songs = self.song_crud.read_by_name(song_name)
                if songs:
                    print(f"\nFound {len(songs)} songs:")
                    for s in songs:
                        self.print_dict(s)
                else:
                    print("No songs found")
            
            elif choice == '5':  # Update
                try:
                    song_id = int(input("Song ID to update: ").strip())
                    print("Enter new values (press Enter to skip):")
                    song_name = input("Song Name: ").strip() or None
                    title = input("Title: ").strip() or None
                    try:
                        duration = int(input("Duration (seconds): ").strip()) if input("Update duration? (y/n): ").strip().lower() == 'y' else None
                    except ValueError:
                        duration = None
                    genre = input("Genre: ").strip() or None
                    release_date = input("Release Date (YYYY-MM-DD): ").strip() or None
                    
                    if self.song_crud.update(song_id, song_name, title, duration, genre, release_date):
                        print("✓ Song updated successfully!")
                    else:
                        print("✗ Failed to update song")
                except ValueError:
                    print("Invalid ID")
            
            elif choice == '6':  # Delete
                try:
                    song_id = int(input("Song ID to delete: ").strip())
                    confirm = input(f"Are you sure you want to delete song {song_id}? (yes/no): ").strip().lower()
                    if confirm == 'yes':
                        if self.song_crud.delete(song_id):
                            print("✓ Song deleted successfully!")
                        else:
                            print("✗ Failed to delete song")
                    else:
                        print("Deletion cancelled")
                except ValueError:
                    print("Invalid ID")
            
            elif choice == '7':  # Link to Artist
                try:
                    song_id = int(input("Song ID: ").strip())
                    artist_id = int(input("Artist ID: ").strip())
                    if self.song_crud.link_artist(song_id, artist_id):
                        print("✓ Song linked to artist successfully!")
                    else:
                        print("✗ Failed to link song to artist")
                except ValueError:
                    print("Invalid ID")
            
            elif choice == '8':
                break
            else:
                print("Invalid choice")
    
    def handle_listener_operations(self):
        """Handle listener CRUD operations"""
        while True:
            self.print_listener_menu()
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':  # Create
                first_name = input("First Name: ").strip()
                last_name = input("Last Name: ").strip()
                date_of_birth = input("Date of Birth (YYYY-MM-DD): ").strip()
                gender = input("Gender: ").strip()
                email = input("Email: ").strip()
                country = input("Country (optional): ").strip() or None
                join_date = input("Join Date (YYYY-MM-DD, optional): ").strip() or None
                account_id = input("Account ID (optional, will create Free if not provided): ").strip()
                account_id = int(account_id) if account_id else None
                
                if self.listener_crud.create(first_name, last_name, date_of_birth, gender, 
                                           email, country, join_date, account_id):
                    print("✓ Listener created successfully!")
                else:
                    print("✗ Failed to create listener")
            
            elif choice == '2':  # Read All
                listeners = self.listener_crud.read_all()
                if listeners:
                    print(f"\nFound {len(listeners)} listeners:")
                    print("-" * 80)
                    for l in listeners:
                        print(f"ID: {l['listener_id']:3d} | {l['listener_first_name']} {l['listener_last_name']} | "
                              f"Email: {l['email']:30s} | Country: {l['country'] or 'N/A'}")
                else:
                    print("No listeners found")
            
            elif choice == '3':  # Read by ID
                try:
                    listener_id = int(input("Listener ID: ").strip())
                    listener = self.listener_crud.read_by_id(listener_id)
                    if listener:
                        self.print_dict(listener)
                    else:
                        print("Listener not found")
                except ValueError:
                    print("Invalid ID")
            
            elif choice == '4':  # Read by Email
                email = input("Email: ").strip()
                listener = self.listener_crud.read_by_email(email)
                if listener:
                    self.print_dict(listener)
                else:
                    print("Listener not found")
            
            elif choice == '5':  # Update
                try:
                    listener_id = int(input("Listener ID to update: ").strip())
                    print("Enter new values (press Enter to skip):")
                    first_name = input("First Name: ").strip() or None
                    last_name = input("Last Name: ").strip() or None
                    date_of_birth = input("Date of Birth (YYYY-MM-DD): ").strip() or None
                    gender = input("Gender: ").strip() or None
                    email = input("Email: ").strip() or None
                    country = input("Country: ").strip() or None
                    account_id = input("Account ID: ").strip()
                    account_id = int(account_id) if account_id else None
                    
                    if self.listener_crud.update(listener_id, first_name, last_name, 
                                               date_of_birth, gender, email, country, account_id):
                        print("✓ Listener updated successfully!")
                    else:
                        print("✗ Failed to update listener")
                except ValueError:
                    print("Invalid ID")
            
            elif choice == '6':  # Delete
                try:
                    listener_id = int(input("Listener ID to delete: ").strip())
                    confirm = input(f"Are you sure you want to delete listener {listener_id}? (yes/no): ").strip().lower()
                    if confirm == 'yes':
                        if self.listener_crud.delete(listener_id):
                            print("✓ Listener deleted successfully!")
                        else:
                            print("✗ Failed to delete listener")
                    else:
                        print("Deletion cancelled")
                except ValueError:
                    print("Invalid ID")
            
            elif choice == '7':
                break
            else:
                print("Invalid choice")
    
    def handle_interaction_operations(self):
        """Handle interaction CRUD operations"""
        while True:
            self.print_interaction_menu()
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':  # Create
                try:
                    listener_id = int(input("Listener ID: ").strip())
                    song_id = int(input("Song ID: ").strip())
                    print("Interaction types: play, like, share, skip")
                    interaction_type = input("Interaction Type: ").strip().lower()
                    if interaction_type not in ['play', 'like', 'share', 'skip']:
                        print("Invalid interaction type")
                        continue
                    timestamp = input("Timestamp (YYYY-MM-DD HH:MM:SS, optional): ").strip() or None
                    
                    if self.interaction_crud.create(listener_id, song_id, interaction_type, timestamp):
                        print("✓ Interaction created successfully!")
                    else:
                        print("✗ Failed to create interaction")
                except ValueError:
                    print("Invalid ID")
            
            elif choice == '2':  # Read All
                interactions = self.interaction_crud.read_all()
                if interactions:
                    print(f"\nFound {len(interactions)} interactions:")
                    print("-" * 100)
                    for i in interactions:
                        print(f"ID: {i['interaction_id']:3d} | {i['listener_first_name']} {i['listener_last_name']} | "
                              f"Song: {i['song_name']:30s} | Type: {i['interaction_type']:5s} | "
                              f"Time: {i['interaction_timestamp']}")
                else:
                    print("No interactions found")
            
            elif choice == '3':  # Read by ID
                try:
                    interaction_id = int(input("Interaction ID: ").strip())
                    interaction = self.interaction_crud.read_by_id(interaction_id)
                    if interaction:
                        self.print_dict(interaction)
                    else:
                        print("Interaction not found")
                except ValueError:
                    print("Invalid ID")
            
            elif choice == '4':  # Read by Listener
                try:
                    listener_id = int(input("Listener ID: ").strip())
                    interactions = self.interaction_crud.read_by_listener(listener_id)
                    if interactions:
                        print(f"\nFound {len(interactions)} interactions:")
                        for i in interactions:
                            self.print_dict(i)
                    else:
                        print("No interactions found")
                except ValueError:
                    print("Invalid ID")
            
            elif choice == '5':  # Read by Song
                try:
                    song_id = int(input("Song ID: ").strip())
                    interactions = self.interaction_crud.read_by_song(song_id)
                    if interactions:
                        print(f"\nFound {len(interactions)} interactions:")
                        for i in interactions:
                            self.print_dict(i)
                    else:
                        print("No interactions found")
                except ValueError:
                    print("Invalid ID")
            
            elif choice == '6':  # Update
                try:
                    interaction_id = int(input("Interaction ID to update: ").strip())
                    print("Enter new values (press Enter to skip):")
                    interaction_type = input("Interaction Type (play/like/share/skip): ").strip().lower() or None
                    timestamp = input("Timestamp (YYYY-MM-DD HH:MM:SS): ").strip() or None
                    
                    if self.interaction_crud.update(interaction_id, interaction_type, timestamp):
                        print("✓ Interaction updated successfully!")
                    else:
                        print("✗ Failed to update interaction")
                except ValueError:
                    print("Invalid ID")
            
            elif choice == '7':  # Delete
                try:
                    interaction_id = int(input("Interaction ID to delete: ").strip())
                    confirm = input(f"Are you sure you want to delete interaction {interaction_id}? (yes/no): ").strip().lower()
                    if confirm == 'yes':
                        if self.interaction_crud.delete(interaction_id):
                            print("✓ Interaction deleted successfully!")
                        else:
                            print("✗ Failed to delete interaction")
                    else:
                        print("Deletion cancelled")
                except ValueError:
                    print("Invalid ID")
            
            elif choice == '8':
                break
            else:
                print("Invalid choice")
    
    def handle_follow_operations(self):
        """Handle follow artist CRUD operations"""
        while True:
            self.print_follow_menu()
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':  # Create
                try:
                    listener_id = int(input("Listener ID: ").strip())
                    artist_id = int(input("Artist ID: ").strip())
                    follow_date = input("Follow Date (YYYY-MM-DD, optional): ").strip() or None
                    
                    if self.follow_crud.create(listener_id, artist_id, follow_date):
                        print("✓ Follow relationship created successfully!")
                    else:
                        print("✗ Failed to create follow relationship")
                except ValueError:
                    print("Invalid ID")
            
            elif choice == '2':  # Read All
                follows = self.follow_crud.read_all()
                if follows:
                    print(f"\nFound {len(follows)} follow relationships:")
                    print("-" * 100)
                    for f in follows:
                        print(f"Listener: {f['listener_first_name']} {f['listener_last_name']} | "
                              f"Artist: {f['artist_first_name']} {f['artist_last_name']} | "
                              f"Follow Date: {f['follow_date']}")
                else:
                    print("No follow relationships found")
            
            elif choice == '3':  # Read by Listener
                try:
                    listener_id = int(input("Listener ID: ").strip())
                    follows = self.follow_crud.read_by_listener(listener_id)
                    if follows:
                        print(f"\nFound {len(follows)} artists followed:")
                        for f in follows:
                            self.print_dict(f)
                    else:
                        print("No artists followed")
                except ValueError:
                    print("Invalid ID")
            
            elif choice == '4':  # Read by Artist
                try:
                    artist_id = int(input("Artist ID: ").strip())
                    follows = self.follow_crud.read_by_artist(artist_id)
                    if follows:
                        print(f"\nFound {len(follows)} followers:")
                        for f in follows:
                            self.print_dict(f)
                    else:
                        print("No followers found")
                except ValueError:
                    print("Invalid ID")
            
            elif choice == '5':  # Delete
                try:
                    listener_id = int(input("Listener ID: ").strip())
                    artist_id = int(input("Artist ID: ").strip())
                    confirm = input(f"Unfollow artist {artist_id}? (yes/no): ").strip().lower()
                    if confirm == 'yes':
                        if self.follow_crud.delete(listener_id, artist_id):
                            print("✓ Unfollowed successfully!")
                        else:
                            print("✗ Failed to unfollow")
                    else:
                        print("Unfollow cancelled")
                except ValueError:
                    print("Invalid ID")
            
            elif choice == '6':
                break
            else:
                print("Invalid choice")
    
    def print_account_type_menu(self):
        """Print account type operations menu"""
        print("\n" + "-"*60)
        print("  ACCOUNT TYPE OPERATIONS")
        print("-"*60)
        print("  1. Create Account Type")
        print("  2. Read All Account Types")
        print("  3. Read Account Type by ID")
        print("  4. Read Account Types by Type")
        print("  5. Update Account Type")
        print("  6. Delete Account Type")
        print("  7. Back to Main Menu")
        print("-"*60)
    
    def print_song_artist_menu(self):
        """Print song-artist relationship operations menu"""
        print("\n" + "-"*60)
        print("  SONG-ARTIST RELATIONSHIP OPERATIONS")
        print("-"*60)
        print("  1. Create Song-Artist Relationship")
        print("  2. Read All Relationships")
        print("  3. Read Artists for a Song")
        print("  4. Read Songs for an Artist")
        print("  5. Delete Song-Artist Relationship")
        print("  6. Back to Main Menu")
        print("-"*60)
    
    def handle_account_type_operations(self):
        """Handle account type CRUD operations"""
        while True:
            self.print_account_type_menu()
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':  # Create
                account_type = input("Account Type (Free/Individual/Family/Duo/Student): ").strip()
                start_date = input("Start Date (YYYY-MM-DD, optional): ").strip() or None
                end_date = input("End Date (YYYY-MM-DD, optional): ").strip() or None
                auto_renew_input = input("Auto Renew (true/false, default: false): ").strip().lower()
                auto_renew = auto_renew_input == 'true' if auto_renew_input else False
                
                account_id = self.account_type_crud.create(account_type, start_date, end_date, auto_renew)
                if account_id:
                    print(f"✓ Account type created successfully! Account ID: {account_id}")
                else:
                    print("✗ Failed to create account type")
            
            elif choice == '2':  # Read All
                accounts = self.account_type_crud.read_all()
                if accounts:
                    print(f"\nFound {len(accounts)} account types:")
                    print("-" * 80)
                    for a in accounts:
                        print(f"ID: {a['account_id']:3d} | Type: {a['account_type']:15s} | "
                              f"Start: {str(a['start_date']) or 'N/A':12s} | "
                              f"End: {str(a['end_date']) or 'N/A':12s} | "
                              f"Auto Renew: {a['auto_renew']}")
                else:
                    print("No account types found")
            
            elif choice == '3':  # Read by ID
                try:
                    account_id = int(input("Account ID: ").strip())
                    account = self.account_type_crud.read_by_id(account_id)
                    if account:
                        self.print_dict(account)
                    else:
                        print("Account type not found")
                except ValueError:
                    print("Invalid ID")
            
            elif choice == '4':  # Read by Type
                account_type = input("Account Type: ").strip()
                accounts = self.account_type_crud.read_by_type(account_type)
                if accounts:
                    print(f"\nFound {len(accounts)} account types:")
                    for a in accounts:
                        self.print_dict(a)
                else:
                    print("No account types found")
            
            elif choice == '5':  # Update
                try:
                    account_id = int(input("Account ID to update: ").strip())
                    print("Enter new values (press Enter to skip):")
                    account_type = input("Account Type: ").strip() or None
                    start_date = input("Start Date (YYYY-MM-DD): ").strip() or None
                    end_date = input("End Date (YYYY-MM-DD): ").strip() or None
                    auto_renew_input = input("Auto Renew (true/false): ").strip().lower()
                    auto_renew = None
                    if auto_renew_input:
                        auto_renew = auto_renew_input == 'true'
                    
                    if self.account_type_crud.update(account_id, account_type, start_date, end_date, auto_renew):
                        print("✓ Account type updated successfully!")
                    else:
                        print("✗ Failed to update account type")
                except ValueError:
                    print("Invalid ID")
            
            elif choice == '6':  # Delete
                try:
                    account_id = int(input("Account ID to delete: ").strip())
                    confirm = input(f"Are you sure you want to delete account type {account_id}? (yes/no): ").strip().lower()
                    if confirm == 'yes':
                        if self.account_type_crud.delete(account_id):
                            print("✓ Account type deleted successfully!")
                        else:
                            print("✗ Failed to delete account type")
                    else:
                        print("Deletion cancelled")
                except ValueError:
                    print("Invalid ID")
            
            elif choice == '7':
                break
            else:
                print("Invalid choice")
    
    def handle_song_artist_operations(self):
        """Handle song-artist relationship CRUD operations"""
        while True:
            self.print_song_artist_menu()
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':  # Create
                try:
                    song_id = int(input("Song ID: ").strip())
                    artist_id = int(input("Artist ID: ").strip())
                    if self.song_artist_crud.create(song_id, artist_id):
                        print("✓ Song-Artist relationship created successfully!")
                    else:
                        print("✗ Failed to create relationship")
                except ValueError:
                    print("Invalid ID")
            
            elif choice == '2':  # Read All
                relationships = self.song_artist_crud.read_all()
                if relationships:
                    print(f"\nFound {len(relationships)} relationships:")
                    print("-" * 100)
                    for r in relationships:
                        print(f"Song: {r['song_name']:30s} | "
                              f"Artist: {r['artist_first_name']} {r['artist_last_name']}")
                else:
                    print("No relationships found")
            
            elif choice == '3':  # Read by Song
                try:
                    song_id = int(input("Song ID: ").strip())
                    relationships = self.song_artist_crud.read_by_song(song_id)
                    if relationships:
                        print(f"\nFound {len(relationships)} artists for this song:")
                        for r in relationships:
                            self.print_dict(r)
                    else:
                        print("No artists found for this song")
                except ValueError:
                    print("Invalid ID")
            
            elif choice == '4':  # Read by Artist
                try:
                    artist_id = int(input("Artist ID: ").strip())
                    relationships = self.song_artist_crud.read_by_artist(artist_id)
                    if relationships:
                        print(f"\nFound {len(relationships)} songs for this artist:")
                        for r in relationships:
                            self.print_dict(r)
                    else:
                        print("No songs found for this artist")
                except ValueError:
                    print("Invalid ID")
            
            elif choice == '5':  # Delete
                try:
                    song_id = int(input("Song ID: ").strip())
                    artist_id = int(input("Artist ID: ").strip())
                    confirm = input(f"Delete relationship between song {song_id} and artist {artist_id}? (yes/no): ").strip().lower()
                    if confirm == 'yes':
                        if self.song_artist_crud.delete(song_id, artist_id):
                            print("✓ Relationship deleted successfully!")
                        else:
                            print("✗ Failed to delete relationship")
                    else:
                        print("Deletion cancelled")
                except ValueError:
                    print("Invalid ID")
            
            elif choice == '6':
                break
            else:
                print("Invalid choice")
    
    def print_dict(self, data: dict):
        """Pretty print a dictionary"""
        print("\n" + "-" * 60)
        for key, value in data.items():
            print(f"  {key}: {value}")
        print("-" * 60)
    
    def run(self):
        """Main run loop"""
        if not self.connect():
            return
        
        try:
            while True:
                self.print_menu()
                choice = input("\nEnter your choice: ").strip()
                
                if choice == '1':
                    self.handle_artist_operations()
                elif choice == '2':
                    self.handle_song_operations()
                elif choice == '3':
                    self.handle_listener_operations()
                elif choice == '4':
                    self.handle_interaction_operations()
                elif choice == '5':
                    self.handle_follow_operations()
                elif choice == '6':
                    self.handle_account_type_operations()
                elif choice == '7':
                    self.handle_song_artist_operations()
                elif choice == '8':
                    print("\nThank you for using Spotify Database Management System!")
                    break
                else:
                    print("Invalid choice. Please try again.")
        except KeyboardInterrupt:
            print("\n\nExiting...")
        finally:
            self.disconnect()


def main():
    """Main entry point"""
    cli = SpotifyCLI()
    cli.run()


if __name__ == "__main__":
    main()

