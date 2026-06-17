#!/usr/bin/env python3
"""
Flask Web Application for Spotify Database
Web-based interface with Spotify theme
"""

# On macOS avoid multiprocessing 'fork' inheritance problems by preferring
# the 'spawn' start method. Set this as early as possible (before other
# imports) so any multiprocessing resources are created with spawn semantics.
try:
    import multiprocessing
    multiprocessing.set_start_method('spawn')
except RuntimeError:
    # already set
    pass
except Exception:
    # ignore other failures; fallback handling exists later
    pass

# Enable faulthandler to capture crashes / native faults to stderr.
try:
    import faulthandler, sys
    faulthandler.enable(all_threads=True)
except Exception:
    pass

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from db_connection import DatabaseConnection
import os
from datetime import date

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for sessions

# Initialize database connection
db = DatabaseConnection()

# Module placeholders; initialize when app starts to avoid sharing resources
# across processes (Flask reloader can fork the process and leak semaphores).
auth = None
complex_queries = None
song_crud = None
song_artist_crud = None
interaction_crud = None
follow_crud = None


def init_app():
    """Initialize DB connection and module instances.

    This is called on startup (and before the first request) so resources
    aren't created at import time where they may be inherited by the
    Flask reloader/child processes, which can cause double-free /
    resource_tracker semaphore warnings on macOS.
    """
    global db, auth, complex_queries, song_crud, song_artist_crud, interaction_crud, follow_crud
    # If already initialized, do nothing
    if auth is not None:
        return

    print("[INIT] init_app starting", flush=True)

    # Import modules here (not at module import time). This keeps
    # potentially heavy imports and any side-effects from running at
    # initialization time where we've already set multiprocessing
    # start method to 'spawn'. It also avoids creating resources in a
    # parent process that could be inherited by the Flask reloader.
    from auth import Authentication
    from artist_dashboard import ArtistDashboard
    from listener_interface import ListenerInterface
    from complex_queries import ComplexQueries
    from crud_operations import SongCRUD, SongArtistCRUD, SongInteractionCRUD, FollowArtistCRUD

    print("[INIT] connecting to database...", flush=True)
    connected = db.connect()
    if not connected:
        print("[INIT] db.connect() returned False", flush=True)
        raise RuntimeError("Failed to connect to the database")
    print("[INIT] database connected", flush=True)

    print("[INIT] creating module instances...", flush=True)
    auth = Authentication(db)
    complex_queries = ComplexQueries(db)
    song_crud = SongCRUD(db)
    song_artist_crud = SongArtistCRUD(db)
    interaction_crud = SongInteractionCRUD(db)
    follow_crud = FollowArtistCRUD(db)
    print("[INIT] module instances created", flush=True)


def _init_app_before_request():
    init_app()

# Register the initializer safely: some environments may not expose
# `before_first_request` as an attribute on the `Flask` instance (rare),
# so use getattr to avoid AttributeError. If unavailable, the app will
# fall back to calling `init_app()` in the `__main__` startup path.
_bf = getattr(app, 'before_first_request', None)
if callable(_bf):
    _bf(_init_app_before_request)

# As an extra-safety for WSGI servers (Waitress, Gunicorn, etc.) ensure
# initialization happens before handling any request. Using `before_request`
# is reliable across different server setups and will call `init_app()` once.
@app.before_request
def _ensure_app_initialized():
    try:
        init_app()
    except Exception:
        # If initialization fails, let the route handlers surface the error
        # (Flask will convert exceptions to 500 responses). Avoid masking
        # the exception so debugging information is preserved.
        raise


# Debug helpers: enabled only when ALLOW_DEBUG_ROUTES=1 in the environment.
# These endpoints help reproduce DB/create issues without dealing with
# browser session cookies. They are intentionally gated by an env var.
if os.environ.get('ALLOW_DEBUG_ROUTES') == '1':
    @app.route('/debug/session')
    def _debug_session():
        # Return session contents for debugging (local/dev only)
        return jsonify({k: session.get(k) for k in session.keys()})

    @app.route('/debug/create-song', methods=['POST'])
    def _debug_create_song():
        # Try to create a song directly using server-side song_crud to
        # reproduce DB errors without browser authentication.
        try:
            init_app()
        except Exception as e:
            return jsonify({'error': f'init_app failed: {e}'}), 500

        data = None
        if request.is_json:
            data = request.get_json(silent=True)
        if not data:
            data = request.form.to_dict() if request.form else {}

        song_name = data.get('song_name')
        if not song_name:
            return jsonify({'error': 'Missing song_name'}), 400

        duration = data.get('duration')
        if duration is not None and duration != '':
            try:
                duration = int(duration)
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid duration'}), 400

        # Perform the insert using a direct pooled connection so we can
        # return low-level errors back to the client for debugging.
        try:
            conn = db.get_connection()
            if conn is None:
                return jsonify({'error': 'Failed to acquire DB connection from pool'}), 500
            cur = conn.cursor()
            insert_q = """
            INSERT INTO song (song_name, title, duration, genre, release_date)
            VALUES (%s, %s, %s, %s, %s)
            """
            params = (song_name, data.get('title'), duration, data.get('genre'), data.get('release_date'))
            cur.execute(insert_q, params)
            conn.commit()
            # fetch last insert id
            cur.execute("SELECT LAST_INSERT_ID() AS id")
            row = cur.fetchone()
            try:
                last_id = row[0] if row else None
            except Exception:
                # In some cursor types fetchone() may return dict; handle that
                last_id = row.get('id') if isinstance(row, dict) else None
            cur.close()
            conn.close()
            if last_id:
                return jsonify({'success': True, 'song_id': int(last_id)})
            else:
                return jsonify({'error': 'Insert succeeded but failed to read last insert id', 'row': row}), 500
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            return jsonify({'error': 'Exception during raw insert', 'exception': str(e), 'trace': tb}), 500


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        
        if user_type == 'artist':
            artist_id = int(request.form.get('artist_id'))
            user = auth.login_artist(artist_id)
            if user:
                session['user_id'] = user['artist_id']
                session['user_type'] = 'artist'
                session['user_name'] = f"{user['artist_first_name']} {user['artist_last_name']}"
                return redirect(url_for('artist_dashboard'))
        
        elif user_type == 'listener':
            email = request.form.get('email')
            listener_id = request.form.get('listener_id')
            
            if email:
                user = auth.login_listener(email=email)
            elif listener_id:
                user = auth.login_listener(listener_id=int(listener_id))
            else:
                return render_template('login.html', error='Please provide email or listener ID')
            
            if user:
                session['user_id'] = user['listener_id']
                session['user_type'] = 'listener'
                session['user_name'] = f"{user['listener_first_name']} {user['listener_last_name']}"
                return redirect(url_for('listener_interface'))
        
        return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('index'))


@app.route('/artist/dashboard')
def artist_dashboard():
    """Artist dashboard page"""
    if 'user_type' not in session or session['user_type'] != 'artist':
        return redirect(url_for('login'))
    
    artist_id = session['user_id']
    
    # Get dashboard data
    # Instrumented logs to help locate native crash source. These prints
    # are intentionally lightweight and flushed immediately so we can see
    # which external call triggers a segmentation fault.
    try:
        print(f"[DEBUG] artist_dashboard: calling auth.login_artist({artist_id})", flush=True)
        artist_info = auth.login_artist(artist_id)
        print("[DEBUG] artist_dashboard: returned from auth.login_artist", flush=True)

        print(f"[DEBUG] artist_dashboard: calling complex_queries.get_artist_follower_count({artist_id})", flush=True)
        follower_stats = complex_queries.get_artist_follower_count(artist_id)
        print("[DEBUG] artist_dashboard: returned from get_artist_follower_count", flush=True)

        print(f"[DEBUG] artist_dashboard: calling complex_queries.get_artist_top_songs({artist_id}, 5)", flush=True)
        top_songs = complex_queries.get_artist_top_songs(artist_id, 5)
        print("[DEBUG] artist_dashboard: returned from get_artist_top_songs", flush=True)

        print(f"[DEBUG] artist_dashboard: calling complex_queries.get_artist_song_performance({artist_id})", flush=True)
        song_performance = complex_queries.get_artist_song_performance(artist_id)
        print("[DEBUG] artist_dashboard: returned from get_artist_song_performance", flush=True)

        print(f"[DEBUG] artist_dashboard: calling complex_queries.get_artist_recent_release_count({artist_id}, 30)", flush=True)
        recent_releases = complex_queries.get_artist_recent_release_count(artist_id, 30)
        print("[DEBUG] artist_dashboard: returned from get_artist_recent_release_count", flush=True)
    except Exception as e:
        # Log and re-raise so Flask can render an error page if possible.
        print(f"[ERROR] artist_dashboard: exception while preparing dashboard: {e}", flush=True)
        raise
    
    # Pass the full song_performance list so template counts reflect
    # the total number of songs for the artist. Previously a slice
    # (`[:10]`) was being passed which caused the "Total Songs" stat
    # to show only the sliced length and not update when new songs
    # were added beyond the slice.
    return render_template('artist_dashboard.html',
                         artist=artist_info,
                         follower_stats=follower_stats,
                         recent_releases=recent_releases,
                         top_songs=top_songs,
                         song_performance=song_performance)


@app.route('/artist/api/performance')
def artist_performance_api():
    """API endpoint for song performance data"""
    if 'user_type' not in session or session['user_type'] != 'artist':
        return jsonify({'error': 'Unauthorized'}), 401
    
    artist_id = session['user_id']
    performance = complex_queries.get_artist_song_performance(artist_id)
    return jsonify(performance)


@app.route('/artist/api/country-distribution')
def artist_country_distribution_api():
    """API endpoint for country distribution"""
    if 'user_type' not in session or session['user_type'] != 'artist':
        return jsonify({'error': 'Unauthorized'}), 401
    
    artist_id = session['user_id']
    distribution = complex_queries.get_artist_country_distribution(artist_id)
    return jsonify(distribution)


@app.route('/artist/api/age-distribution')
def artist_age_distribution_api():
    """API endpoint for age group distribution"""
    if 'user_type' not in session or session['user_type'] != 'artist':
        return jsonify({'error': 'Unauthorized'}), 401
    
    artist_id = session['user_id']
    distribution = complex_queries.get_artist_age_group_distribution(artist_id)
    return jsonify(distribution)


@app.route('/artist/api/gender-distribution')
def artist_gender_distribution_api():
    """API endpoint for gender distribution"""
    if 'user_type' not in session or session['user_type'] != 'artist':
        return jsonify({'error': 'Unauthorized'}), 401
    
    artist_id = session['user_id']
    distribution = complex_queries.get_artist_gender_distribution(artist_id)
    return jsonify(distribution)


@app.route('/artist/api/monthly-growth')
def artist_monthly_growth_api():
    """API endpoint for monthly follower growth"""
    if 'user_type' not in session or session['user_type'] != 'artist':
        return jsonify({'error': 'Unauthorized'}), 401
    
    artist_id = session['user_id']
    growth = complex_queries.get_artist_monthly_follower_growth(artist_id)
    return jsonify(growth)


@app.route('/artist/upload-song', methods=['POST'])
def upload_song():
    """Upload a new song"""
    if 'user_type' not in session or session['user_type'] != 'artist':
        return jsonify({'error': 'Unauthorized'}), 401
    
    artist_id = session.get('user_id')

    # Debug logging: print request info to help diagnose 400s
    try:
        print("[UPLOAD] request received", flush=True)
        print(f"[UPLOAD] session: user_type={session.get('user_type')}, user_id={session.get('user_id')}", flush=True)
        print(f"[UPLOAD] content_type={request.content_type}", flush=True)
        # headers can be large; print a filtered subset
        headers_to_log = {k: request.headers.get(k) for k in ['Content-Type', 'Content-Length', 'Cookie', 'User-Agent']}
        print(f"[UPLOAD] headers: {headers_to_log}", flush=True)
        raw_body = request.get_data(cache=True, as_text=True)
        print(f"[UPLOAD] raw_body (first 200 chars): {raw_body[:200]!s}", flush=True)
    except Exception as e:
        print(f"[UPLOAD] failed to log request metadata: {e}", flush=True)

    # Accept JSON or form-encoded data for compatibility with different clients
    data = None
    if request.is_json:
        data = request.get_json(silent=True)
    if not data:
        # Fallback to form data
        data = request.form.to_dict() if request.form else {}

    print(f"[UPLOAD] parsed data: {data}", flush=True)

    # Basic validation
    song_name = data.get('song_name')
    if not song_name:
        print("[UPLOAD] missing song_name -> 400", flush=True)
        return jsonify({'error': 'Missing required field: song_name'}), 400

    title = data.get('title')
    duration = data.get('duration')
    genre = data.get('genre')
    release_date = data.get('release_date')

    # If release_date isn't provided, default to today so the song shows
    # up in "new" queries that filter by recent release_date.
    if not release_date:
        release_date = date.today().isoformat()  # YYYY-MM-DD
        print(f"[UPLOAD] release_date not provided; defaulting to {release_date}", flush=True)

    # Coerce duration to int when possible
    if duration is not None and duration != '':
        try:
            duration = int(duration)
        except (ValueError, TypeError):
            print(f"[UPLOAD] invalid duration={duration} -> 400", flush=True)
            return jsonify({'error': 'Invalid duration; must be integer seconds'}), 400

    try:
        song_id = song_crud.create(
            song_name=song_name,
            title=title,
            duration=duration,
            genre=genre,
            release_date=release_date
        )
    except Exception as e:
        print(f"[ERROR] upload_song: exception creating song: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal error while creating song'}), 500

    if song_id:
        try:
            song_artist_crud.create(song_id, artist_id)
        except Exception as e:
            print(f"[ERROR] upload_song: exception linking song to artist: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return jsonify({'error': 'Song created but failed to link to artist'}), 500
        print(f"[UPLOAD] song created id={song_id} (release_date={release_date})", flush=True)
        return jsonify({'success': True, 'song_id': song_id})
    else:
        print("[UPLOAD] song_crud.create returned falsy -> 400", flush=True)
        return jsonify({'error': 'Failed to create song'}), 400


@app.route('/listener/interface')
def listener_interface():
    """Listener interface page"""
    if 'user_type' not in session or session['user_type'] != 'listener':
        return redirect(url_for('login'))
    
    listener_id = session['user_id']
    
    # Get interface data
    new_songs = complex_queries.get_new_songs(20, 30)
    followed_songs = complex_queries.get_followed_artists_songs(listener_id, 20)
    recommendations = complex_queries.get_listener_recommendations(listener_id, 10)
    # If personalized recommendations are empty, fall back to global top songs
    if not recommendations:
        recommendations = complex_queries.get_global_top_songs(10) or []
    stats = complex_queries.get_listener_statistics(listener_id)
    followed_artists = follow_crud.read_by_listener(listener_id)
    # Get liked songs: read interactions and filter likes, keep latest like per song
    liked_interactions = interaction_crud.read_by_listener(listener_id) or []
    liked_songs_map = {}
    for it in liked_interactions:
        if it.get('interaction_type') != 'like':
            continue
        sid = it.get('song_id')
        ts = it.get('interaction_timestamp')
        # keep most recent like per song
        if sid not in liked_songs_map or (ts and liked_songs_map[sid].get('interaction_timestamp') < ts):
            liked_songs_map[sid] = {
                'song_id': sid,
                'song_name': it.get('song_name'),
                'liked_at': ts
            }
    liked_songs = list(liked_songs_map.values())
    
    return render_template('listener_interface.html',
                         new_songs=new_songs,
                         followed_songs=followed_songs,
                         recommendations=recommendations,
                         stats=stats,
                         followed_artists=followed_artists,
                         liked_songs=liked_songs)


@app.route('/listener/api/interact', methods=['POST'])
def listener_interact():
    """Handle song interactions (play, like, share)"""
    if 'user_type' not in session or session['user_type'] != 'listener':
        return jsonify({'error': 'Unauthorized'}), 401
    
    listener_id = session['user_id']
    data = request.json
    
    interaction_type = data.get('interaction_type')
    song_id = data.get('song_id')
    
    if interaction_type not in ['play', 'like', 'share', 'skip']:
        return jsonify({'error': 'Invalid interaction type'}), 400
    
    success = interaction_crud.create(listener_id, song_id, interaction_type)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to record interaction'}), 400


@app.route('/listener/api/follow', methods=['POST'])
def listener_follow():
    """Follow an artist"""
    if 'user_type' not in session or session['user_type'] != 'listener':
        return jsonify({'error': 'Unauthorized'}), 401
    
    listener_id = session['user_id']
    data = request.json
    artist_id = data.get('artist_id')
    
    success = follow_crud.create(listener_id, artist_id)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to follow artist'}), 400


@app.route('/listener/api/unfollow', methods=['POST'])
def listener_unfollow():
    """Unfollow an artist"""
    if 'user_type' not in session or session['user_type'] != 'listener':
        return jsonify({'error': 'Unauthorized'}), 401
    
    listener_id = session['user_id']
    data = request.json
    artist_id = data.get('artist_id')
    
    success = follow_crud.delete(listener_id, artist_id)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to unfollow artist'}), 400


@app.route('/api/artists')
def api_artists():
    """Get list of artists for selection"""
    artists = auth.list_artists()
    return jsonify(artists)


if __name__ == '__main__':
    # If the Flask instance doesn't support `before_first_request` (older
    # environments), initialize modules here in the main process. When the
    # reloader is enabled, Flask will call the registered before-first-request
    # handler in the child process, so avoid initializing in the parent.
    if not callable(getattr(app, 'before_first_request', None)):
        init_app()

    # On macOS the default 'fork' start method for multiprocessing can cause
    # semaphore handles to be inherited by child processes leading to
    # "Double free" / resource_tracker warnings. Prefer 'spawn' when possible.
    try:
        import multiprocessing
        multiprocessing.set_start_method('spawn')
    except RuntimeError:
        # start method already set; ignore
        pass
    except Exception:
        # If anything else goes wrong, ignore and continue; see notes below.
        pass

    # Bind to localhost only so the app is not reachable from the LAN.
    # Using '127.0.0.1' prevents remote machines from connecting.
    # Disable the Flask reloader here for local debugging of multiprocessing
    # related issues — the reloader forks and can cause resource inheritance
    # on macOS. Set `debug=False` and `use_reloader=False` for stability.
    app.run(debug=False, use_reloader=False, host='127.0.0.1', port=5001)

