"""
Listener Interface
Provides browsing, interaction, and discovery features for listeners
"""

from db_connection import DatabaseConnection
from crud_operations import ListenerCRUD, SongInteractionCRUD, FollowArtistCRUD
from complex_queries import ComplexQueries
from typing import Dict


class ListenerInterface:
    """Listener interface with browsing and interaction features"""
    
    def __init__(self, db: DatabaseConnection, listener_id: int):
        self.db = db
        self.listener_id = listener_id
        self.listener_crud = ListenerCRUD(db)
        self.interaction_crud = SongInteractionCRUD(db)
        self.follow_crud = FollowArtistCRUD(db)
        self.complex_queries = ComplexQueries(db)
        self.listener_info = None
    
    def load_listener_info(self):
        """Load listener information"""
        self.listener_info = self.listener_crud.read_by_id(self.listener_id)
        return self.listener_info
    
    def print_header(self):
        """Print interface header"""
        if not self.listener_info:
            self.load_listener_info()
        
        print("\n" + "="*80)
        print(f"  SPOTIFY - Welcome {self.listener_info['listener_first_name']} {self.listener_info['listener_last_name']}")
        print("="*80)
    
    def print_main_menu(self):
        """Print main menu"""
        print("\nMain Menu:")
        print("  1. Browse New Songs")
        print("  2. Songs from Followed Artists")
        print("  3. Get Recommendations")
        print("  4. Play a Song")
        print("  5. Like a Song")
        print("  6. Share a Song")
        print("  7. Follow an Artist")
        print("  8. Unfollow an Artist")
        print("  9. View My Statistics")
        print("  10. View My Followed Artists")
        print("  11. View My Liked Songs")
        print("  12. View My Interactions")
        print("  13. Exit")
        print("="*80)
    
    def browse_new_songs(self):
        """Browse newly released songs"""
        print("\n" + "-"*80)
        print("  NEW SONGS")
        print("-"*80)
        
        try:
            days = int(input("Show songs from last N days (default 30): ").strip() or "30")
            limit = int(input("Number of songs to show (default 20): ").strip() or "20")
        except ValueError:
            days = 30
            limit = 20
        
        songs = self.complex_queries.get_new_songs(limit, days)
        if songs:
            print(f"\n{'Song Name':<30} {'Artists':<25} {'Genre':<15} {'Listeners':<10} {'Interactions':<12}")
            print("-"*100)
            for song in songs:
                print(f"{song['song_name'][:28]:<30} {song['artists'][:23]:<25} "
                      f"{song['genre'] or 'N/A':<15} {song['listener_count']:<10} {song['interaction_count']:<12}")
            
            # Option to interact with a song
            try:
                song_id = input("\nEnter Song ID to interact (or press Enter to skip): ").strip()
                if song_id:
                    self._interact_with_song(int(song_id))
            except ValueError:
                pass
        else:
            print("No new songs found")
    
    def view_followed_artists_songs(self):
        """View songs from followed artists"""
        print("\n" + "-"*80)
        print("  SONGS FROM FOLLOWED ARTISTS")
        print("-"*80)
        
        songs = self.complex_queries.get_followed_artists_songs(self.listener_id, 20)
        if songs:
            print(f"\n{'Song Name':<30} {'Artist':<25} {'Genre':<15} {'Release Date':<12} {'Popularity':<12}")
            print("-"*100)
            for song in songs:
                print(f"{song['song_name'][:28]:<30} {song['artist_name'][:23]:<25} "
                      f"{song['genre'] or 'N/A':<15} {str(song['release_date'] or 'N/A'):<12} "
                      f"{song['total_interactions']:<12}")
            
            try:
                song_id = input("\nEnter Song ID to interact (or press Enter to skip): ").strip()
                if song_id:
                    self._interact_with_song(int(song_id))
            except ValueError:
                pass
        else:
            print("No songs from followed artists found. Follow some artists first!")
    
    def get_recommendations(self):
        """Get personalized song recommendations"""
        print("\n" + "-"*80)
        print("  RECOMMENDED FOR YOU")
        print("-"*80)
        
        recommendations = self.complex_queries.get_listener_recommendations(self.listener_id, 10)
        if recommendations:
            print(f"\n{'Song Name':<30} {'Artists':<25} {'Genre':<15} {'Popularity':<12}")
            print("-"*85)
            for rec in recommendations:
                print(f"{rec['song_name'][:28]:<30} {rec['artists'][:23]:<25} "
                      f"{rec['genre'] or 'N/A':<15} {rec['popularity_count']:<12}")
            
            try:
                song_id = input("\nEnter Song ID to interact (or press Enter to skip): ").strip()
                if song_id:
                    self._interact_with_song(int(song_id))
            except ValueError:
                pass
        else:
            print("No recommendations available. Start listening to songs to get recommendations!")
    
    def play_song(self):
        """Play a song (record play interaction)"""
        try:
            song_id = int(input("Enter Song ID to play: ").strip())
            if self.interaction_crud.create(self.listener_id, song_id, 'play'):
                print("✓ Song played! Interaction recorded.")
            else:
                print("✗ Failed to record play interaction")
        except ValueError:
            print("Invalid Song ID")
    
    def like_song(self):
        """Like a song"""
        try:
            song_id = int(input("Enter Song ID to like: ").strip())
            if self.interaction_crud.create(self.listener_id, song_id, 'like'):
                print("✓ Song liked!")
            else:
                print("✗ Failed to like song (may already be liked)")
        except ValueError:
            print("Invalid Song ID")
    
    def share_song(self):
        """Share a song"""
        try:
            song_id = int(input("Enter Song ID to share: ").strip())
            if self.interaction_crud.create(self.listener_id, song_id, 'share'):
                print("✓ Song shared!")
            else:
                print("✗ Failed to share song")
        except ValueError:
            print("Invalid Song ID")
    
    def follow_artist(self):
        """Follow an artist"""
        try:
            artist_id = int(input("Enter Artist ID to follow: ").strip())
            if self.follow_crud.create(self.listener_id, artist_id):
                print("✓ Now following artist!")
            else:
                print("✗ Failed to follow artist (may already be following)")
        except ValueError:
            print("Invalid Artist ID")
    
    def unfollow_artist(self):
        """Unfollow an artist"""
        followed = self.follow_crud.read_by_listener(self.listener_id)
        if not followed:
            print("You are not following any artists")
            return
        
        print("\nArtists you follow:")
        for i, artist in enumerate(followed, 1):
            print(f"{i}. {artist['artist_first_name']} {artist['artist_last_name']} (ID: {artist['artist_id']})")
        
        try:
            artist_id = int(input("\nEnter Artist ID to unfollow: ").strip())
            if self.follow_crud.delete(self.listener_id, artist_id):
                print("✓ Unfollowed artist")
            else:
                print("✗ Failed to unfollow artist")
        except ValueError:
            print("Invalid Artist ID")
    
    def view_statistics(self):
        """View listener statistics"""
        print("\n" + "-"*80)
        print("  YOUR STATISTICS")
        print("-"*80)
        
        stats = self.complex_queries.get_listener_statistics(self.listener_id)
        if stats:
            print(f"\n  Unique Songs Played: {stats['unique_songs_played']}")
            print(f"  Total Interactions: {stats['total_interactions']}")
            print(f"  Total Plays: {stats['total_plays']}")
            print(f"  Total Likes: {stats['total_likes']}")
            print(f"  Total Shares: {stats['total_shares']}")
            print(f"  Unique Artists Listened: {stats['unique_artists_listened']}")
            print(f"  Artists Followed: {stats['artists_followed']}")
            print(f"  Genres Explored: {stats['genres_explored']}")
        else:
            print("No statistics available")
    
    def view_followed_artists(self):
        """View followed artists"""
        print("\n" + "-"*80)
        print("  FOLLOWED ARTISTS")
        print("-"*80)
        
        followed = self.follow_crud.read_by_listener(self.listener_id)
        if followed:
            print(f"\n{'Artist Name':<30} {'Follow Date':<12}")
            print("-"*45)
            for artist in followed:
                print(f"{artist['artist_first_name']} {artist['artist_last_name']:<30} "
                      f"{artist['follow_date']:<12}")
        else:
            print("You are not following any artists")

    def view_liked_songs(self):
        """View songs the listener has liked"""
        print("\n" + "-"*80)
        print("  LIKED SONGS")
        print("-"*80)

        interactions = self.interaction_crud.read_by_listener(self.listener_id)
        if not interactions:
            print("You have no interactions yet")
            return

        # Filter for 'like' interactions and keep latest like per song
        liked = [i for i in interactions if i.get('interaction_type') == 'like']
        if not liked:
            print("You haven't liked any songs yet")
            return

        # Optionally, deduplicate by song_id and show the most recent like
        liked_by_song = {}
        for it in liked:
            song_id = it.get('song_id')
            ts = it.get('interaction_timestamp')
            # choose latest timestamp
            if song_id not in liked_by_song or (ts and liked_by_song[song_id].get('interaction_timestamp') < ts):
                liked_by_song[song_id] = it

        liked_list = list(liked_by_song.values())
        print(f"\n{'Song ID':<8} {'Song Name':<30} {'Liked At':<20}")
        print("-"*60)
        for it in liked_list:
            song_name = it.get('song_name') or 'Unknown'
            print(f"{it.get('song_id'):<8} {song_name[:28]:<30} {str(it.get('interaction_timestamp')):<20}")
    
    def view_interactions(self):
        """View listener's interactions"""
        print("\n" + "-"*80)
        print("  YOUR INTERACTIONS")
        print("-"*80)
        
        interactions = self.interaction_crud.read_by_listener(self.listener_id)
        if interactions:
            print(f"\n{'Song Name':<30} {'Type':<10} {'Timestamp':<20}")
            print("-"*65)
            for interaction in interactions[:50]:  # Show last 50
                print(f"{interaction['song_name'][:28]:<30} {interaction['interaction_type']:<10} "
                      f"{str(interaction['interaction_timestamp']):<20}")
        else:
            print("No interactions found")
    
    def _interact_with_song(self, song_id: int):
        """Helper method to interact with a song"""
        print("\nWhat would you like to do?")
        print("  1. Play")
        print("  2. Like")
        print("  3. Share")
        print("  4. Cancel")
        
        choice = input("Enter choice: ").strip()
        if choice == '1':
            if self.interaction_crud.create(self.listener_id, song_id, 'play'):
                print("✓ Song played!")
        elif choice == '2':
            if self.interaction_crud.create(self.listener_id, song_id, 'like'):
                print("✓ Song liked!")
            else:
                print("✗ Failed to like (may already be liked)")
        elif choice == '3':
            if self.interaction_crud.create(self.listener_id, song_id, 'share'):
                print("✓ Song shared!")
        elif choice == '4':
            return
    
    def run(self):
        """Run the listener interface"""
        if not self.load_listener_info():
            print("✗ Listener not found")
            return
        
        while True:
            self.print_header()
            self.print_main_menu()
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                self.browse_new_songs()
            elif choice == '2':
                self.view_followed_artists_songs()
            elif choice == '3':
                self.get_recommendations()
            elif choice == '4':
                self.play_song()
            elif choice == '5':
                self.like_song()
            elif choice == '6':
                self.share_song()
            elif choice == '7':
                self.follow_artist()
            elif choice == '8':
                self.unfollow_artist()
            elif choice == '9':
                self.view_statistics()
            elif choice == '10':
                self.view_followed_artists()
            elif choice == '11':
                self.view_liked_songs()
            elif choice == '12':
                self.view_interactions()
            elif choice == '13':
                print("\nThank you for using Spotify!")
                break
            else:
                print("Invalid choice")
            
            input("\nPress Enter to continue...")

