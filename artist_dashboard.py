"""
Artist Dashboard Interface
Provides analytics and management features for artists
"""

from db_connection import DatabaseConnection
from crud_operations import ArtistCRUD, SongCRUD, SongArtistCRUD
from complex_queries import ComplexQueries
from typing import Dict


class ArtistDashboard:
    """Artist dashboard with performance analytics and song management"""
    
    def __init__(self, db: DatabaseConnection, artist_id: int):
        self.db = db
        self.artist_id = artist_id
        self.artist_crud = ArtistCRUD(db)
        self.song_crud = SongCRUD(db)
        self.song_artist_crud = SongArtistCRUD(db)
        self.complex_queries = ComplexQueries(db)
        self.artist_info = None
    
    def load_artist_info(self):
        """Load artist information"""
        self.artist_info = self.artist_crud.read_by_id(self.artist_id)
        return self.artist_info
    
    def print_dashboard_header(self):
        """Print dashboard header"""
        if not self.artist_info:
            self.load_artist_info()
        
        print("\n" + "="*80)
        print(f"  ARTIST DASHBOARD - {self.artist_info['artist_first_name']} {self.artist_info['artist_last_name']}")
        print("="*80)
    
    def print_main_menu(self):
        """Print main menu"""
        print("\nMain Menu:")
        print("  1. View Profile")
        print("  2. Upload New Song")
        print("  3. View Song Performance")
        print("  4. View Followers")
        print("  5. View Country Distribution")
        print("  6. View Age Group Distribution")
        print("  7. View Gender Distribution")
        print("  8. View Top Songs")
        print("  9. View Monthly Follower Growth")
        print("  10. View Performance by Country & Genre (OLAP)")
        print("  11. Exit")
        print("="*80)
    
    def view_profile(self):
        """View and edit artist profile"""
        if not self.artist_info:
            self.load_artist_info()
        
        print("\n" + "-"*80)
        print("  ARTIST PROFILE")
        print("-"*80)
        print(f"  ID: {self.artist_info['artist_id']}")
        print(f"  Name: {self.artist_info['artist_first_name']} {self.artist_info['artist_last_name']}")
        print(f"  Country: {self.artist_info['country'] or 'N/A'}")
        print(f"  Genre: {self.artist_info['genre'] or 'N/A'}")
        print(f"  Bio: {self.artist_info['bio'] or 'N/A'}")
        print(f"  Join Date: {self.artist_info['join_date'] or 'N/A'}")
        print("-"*80)
        
        edit = input("\nEdit profile? (y/n): ").strip().lower()
        if edit == 'y':
            print("\nEnter new values (press Enter to skip):")
            first_name = input("First Name: ").strip() or None
            last_name = input("Last Name: ").strip() or None
            country = input("Country: ").strip() or None
            bio = input("Bio: ").strip() or None
            genre = input("Genre: ").strip() or None
            
            if self.artist_crud.update(self.artist_id, first_name, last_name, 
                                     country, bio, genre):
                print("✓ Profile updated successfully!")
                self.load_artist_info()
            else:
                print("✗ Failed to update profile")
    
    def upload_song(self):
        """Upload a new song"""
        print("\n" + "-"*80)
        print("  UPLOAD NEW SONG")
        print("-"*80)
        
        song_name = input("Song Name: ").strip()
        if not song_name:
            print("✗ Song name is required")
            return
        
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
            
            # Automatically link to artist
            if self.song_artist_crud.create(song_id, self.artist_id):
                print(f"✓ Song linked to your artist profile!")
            else:
                print("⚠ Song created but failed to link to artist. Please link manually.")
        else:
            print("✗ Failed to create song")
    
    def view_song_performance(self):
        """View detailed song performance metrics"""
        print("\n" + "-"*80)
        print("  SONG PERFORMANCE METRICS")
        print("-"*80)
        
        songs = self.complex_queries.get_artist_song_performance(self.artist_id)
        if songs:
            print(f"\n{'Song Name':<30} {'Plays':<8} {'Likes':<8} {'Shares':<8} {'Skips':<8} {'Engagement':<12} {'Skip Rate':<10}")
            print("-"*100)
            for song in songs:
                print(f"{song['song_name'][:28]:<30} {song['total_plays']:<8} {song['total_likes']:<8} "
                      f"{song['total_shares']:<8} {song['total_skips']:<8} "
                      f"{song['engagement_rate']:<12} {song['skip_rate']:<10}")
            
            # Show detailed view for a specific song
            try:
                song_id = input("\nEnter Song ID for detailed view (or press Enter to skip): ").strip()
                if song_id:
                    song_id = int(song_id)
                    song = next((s for s in songs if s['song_id'] == song_id), None)
                    if song:
                        print("\n" + "-"*80)
                        print("  DETAILED SONG METRICS")
                        print("-"*80)
                        for key, value in song.items():
                            print(f"  {key}: {value}")
                    else:
                        print("Song not found")
            except ValueError:
                pass
        else:
            print("No songs found or no performance data available")
    
    def view_followers(self):
        """View follower statistics"""
        print("\n" + "-"*80)
        print("  FOLLOWER STATISTICS")
        print("-"*80)
        
        stats = self.complex_queries.get_artist_follower_count(self.artist_id)
        if stats:
            print(f"\n  Total Followers: {stats['total_followers']}")
            print(f"  New Followers (Last 30 days): {stats['new_followers_30d']}")
            print(f"  New Followers (Last 7 days): {stats['new_followers_7d']}")
        else:
            print("No follower data available")
    
    def view_country_distribution(self):
        """View listener distribution by country"""
        print("\n" + "-"*80)
        print("  LISTENER DISTRIBUTION BY COUNTRY")
        print("-"*80)
        
        countries = self.complex_queries.get_artist_country_distribution(self.artist_id)
        if countries:
            print(f"\n{'Country':<20} {'Listeners':<12} {'Interactions':<12} {'Plays':<10} {'Likes':<10} {'Percentage':<12}")
            print("-"*90)
            for country in countries:
                print(f"{country['country'] or 'Unknown':<20} {country['unique_listeners']:<12} "
                      f"{country['total_interactions']:<12} {country['total_plays']:<10} "
                      f"{country['total_likes']:<10} {country['percentage_of_listeners'] or 0:<12}")
        else:
            print("No country distribution data available")
    
    def view_age_distribution(self):
        """View listener distribution by age groups"""
        print("\n" + "-"*80)
        print("  LISTENER DISTRIBUTION BY AGE GROUP")
        print("-"*80)
        
        age_groups = self.complex_queries.get_artist_age_group_distribution(self.artist_id)
        if age_groups:
            print(f"\n{'Age Group':<15} {'Listeners':<12} {'Total Interactions':<18} {'Avg per Listener':<18}")
            print("-"*70)
            for age in age_groups:
                print(f"{age['age_group']:<15} {age['unique_listeners']:<12} "
                      f"{age['total_interactions']:<18} {float(age['avg_interactions_per_listener'] or 0):.2f}")
        else:
            print("No age group distribution data available")
    
    def view_gender_distribution(self):
        """View listener distribution by gender"""
        print("\n" + "-"*80)
        print("  LISTENER DISTRIBUTION BY GENDER")
        print("-"*80)
        
        genders = self.complex_queries.get_artist_gender_distribution(self.artist_id)
        if genders:
            print(f"\n{'Gender':<15} {'Listeners':<12} {'Interactions':<12} {'Likes':<10} {'Like %':<10}")
            print("-"*65)
            for gender in genders:
                print(f"{gender['gender']:<15} {gender['unique_listeners']:<12} "
                      f"{gender['total_interactions']:<12} {gender['total_likes']:<10} "
                      f"{gender['like_percentage'] or 0:<10}")
        else:
            print("No gender distribution data available")
    
    def view_top_songs(self):
        """View top performing songs"""
        print("\n" + "-"*80)
        print("  TOP PERFORMING SONGS")
        print("-"*80)
        
        try:
            limit = int(input("Number of songs to display (default 10): ").strip() or "10")
        except ValueError:
            limit = 10
        
        songs = self.complex_queries.get_artist_top_songs(self.artist_id, limit)
        if songs:
            print(f"\n{'Rank':<6} {'Song Name':<30} {'Plays':<8} {'Likes':<8} {'Shares':<8} {'Total':<8}")
            print("-"*80)
            for i, song in enumerate(songs, 1):
                print(f"{i:<6} {song['song_name'][:28]:<30} {song['plays']:<8} "
                      f"{song['likes']:<8} {song['shares']:<8} {song['total_interactions']:<8}")
        else:
            print("No songs found")
    
    def view_monthly_growth(self):
        """View monthly follower growth"""
        print("\n" + "-"*80)
        print("  MONTHLY FOLLOWER GROWTH")
        print("-"*80)
        
        growth = self.complex_queries.get_artist_monthly_follower_growth(self.artist_id)
        if growth:
            print(f"\n{'Month':<12} {'New Followers':<15} {'Previous Month':<15} {'Change':<10} {'Growth %':<12}")
            print("-"*70)
            for month in growth:
                print(f"{month['follow_month']:<12} {month['new_follows']:<15} "
                      f"{month['previous_month_follows']:<15} {month['follow_change']:<10} "
                      f"{month['growth_percentage'] or 'N/A':<12}")
        else:
            print("No growth data available")
    
    def view_olap_analysis(self):
        """View OLAP analysis by country and genre"""
        print("\n" + "-"*80)
        print("  PERFORMANCE BY COUNTRY & GENRE (OLAP)")
        print("-"*80)
        
        analysis = self.complex_queries.get_artist_performance_by_country_and_genre(self.artist_id)
        if analysis:
            print(f"\n{'Country':<20} {'Genre':<20} {'Interactions':<12} {'Plays':<10} {'Likes':<10} {'Avg Duration':<12}")
            print("-"*100)
            for row in analysis:
                country = row['country'] or 'All Countries'
                genre = row['genre'] or 'All Genres'
                print(f"{country:<20} {genre:<20} {row['total_interactions']:<12} "
                      f"{row['plays']:<10} {row['likes']:<10} {float(row['avg_song_duration'] or 0):.2f}")
        else:
            print("No OLAP data available")
    
    def run(self):
        """Run the artist dashboard"""
        if not self.load_artist_info():
            print("✗ Artist not found")
            return
        
        while True:
            self.print_dashboard_header()
            self.print_main_menu()
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                self.view_profile()
            elif choice == '2':
                self.upload_song()
            elif choice == '3':
                self.view_song_performance()
            elif choice == '4':
                self.view_followers()
            elif choice == '5':
                self.view_country_distribution()
            elif choice == '6':
                self.view_age_distribution()
            elif choice == '7':
                self.view_gender_distribution()
            elif choice == '8':
                self.view_top_songs()
            elif choice == '9':
                self.view_monthly_growth()
            elif choice == '10':
                self.view_olap_analysis()
            elif choice == '11':
                print("\nLogging out...")
                break
            else:
                print("Invalid choice")
            
            input("\nPress Enter to continue...")

