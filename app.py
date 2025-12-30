#!/usr/bin/env python3
"""W3GH - Spotify AutoPlayer Web Interface"""
import os
import logging
import threading
import time
from flask import Flask, render_template, jsonify, request, redirect
from spotipy.oauth2 import SpotifyOAuth
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)

spotify_service = None
autoplay_thread = None
autoplay_thread_lock = threading.Lock()

def get_spotify_service():
    global spotify_service
    if spotify_service is None:
        from spotify_service import SpotifyService
        spotify_service = SpotifyService()
    # Always ensure connected
    spotify_service.ensure_connected()
    return spotify_service


def autoplay_loop():
    logger.info("Autoplay thread started.")
    while True:
        try:
            svc = get_spotify_service()
            if not svc.is_connected():
                logger.warning("Spotify not connected. Retrying in 30 seconds...")
                time.sleep(30)
                continue

            Config.apply_settings()
            svc.check_and_autoplay()

            status = svc.get_status()
            if status.get('playback'):
                pb = status['playback']
                state = "AUTOPLAY" if svc.autoplay_mode else "USER"
                logger.info(f"[{state}] {pb['artist']} - {pb['track']} on {pb['device']}")
            elif status.get('stopped_since_minutes'):
                logger.info(
                    "[STOPPED] for %.1f min (trigger at %s min)",
                    status['stopped_since_minutes'],
                    status['idle_minutes']
                )
            else:
                logger.debug("No playback")

            settings = Config.load_settings()
            check_interval = settings.get('check_interval_seconds', 30)
            time.sleep(max(5, int(check_interval)))

        except Exception as e:
            logger.error(f"Error in autoplay loop: {e}")
            time.sleep(10)


def start_autoplay_thread():
    global autoplay_thread
    with autoplay_thread_lock:
        if autoplay_thread and autoplay_thread.is_alive():
            return
        autoplay_thread = threading.Thread(target=autoplay_loop, daemon=True)
        autoplay_thread.start()


def get_auth_manager():
    try:
        client_id = Config.get_client_id()
        client_secret = Config.get_client_secret()
    except:
        return None

    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=Config.SPOTIFY_REDIRECT_URI,
        scope=Config.SPOTIFY_SCOPE,
        cache_path=Config.CACHE_FILE,
        open_browser=False
    )


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/auth/status')
def auth_status():
    has_credentials = os.path.exists(Config.CREDENTIALS_FILE)
    has_token = os.path.exists(Config.CACHE_FILE)

    token_valid = False
    if has_token:
        try:
            auth_manager = get_auth_manager()
            if auth_manager:
                token_info = auth_manager.get_cached_token()
                if token_info and not auth_manager.is_token_expired(token_info):
                    token_valid = True
        except:
            pass

    return jsonify({
        'has_credentials': has_credentials,
        'has_token': has_token,
        'token_valid': token_valid,
        'redirect_uri': Config.SPOTIFY_REDIRECT_URI
    })


@app.route('/auth/setup', methods=['POST'])
def auth_setup():
    data = request.json
    client_id = data.get('client_id', '').strip()
    client_secret = data.get('client_secret', '').strip()

    if not client_id or not client_secret:
        return jsonify({'success': False, 'error': 'Client ID ve Secret gerekli'})

    Config.save_credentials(client_id, client_secret)
    return jsonify({'success': True})


@app.route('/auth/login')
def auth_login():
    auth_manager = get_auth_manager()
    if not auth_manager:
        return redirect('/spo/?error=no_credentials')

    auth_url = auth_manager.get_authorize_url()
    return redirect(auth_url)


@app.route('/auth/callback')
def auth_callback():
    code = request.args.get('code')
    error = request.args.get('error')

    if error:
        return redirect(f'/spo/?error={error}')

    if not code:
        return redirect('/spo/?error=no_code')

    auth_manager = get_auth_manager()
    if not auth_manager:
        return redirect('/spo/?error=no_credentials')

    try:
        token_info = auth_manager.get_access_token(code, as_dict=True, check_cache=False)

        global spotify_service
        if spotify_service:
            spotify_service._initialized = False
            spotify_service.sp = None
            spotify_service.user_info = None

        return redirect('/spo/?success=1')
    except Exception as e:
        logger.error(f"Auth callback error: {e}")
        return redirect(f'/spo/?error=token_error')


@app.route('/auth/logout', methods=['POST'])
def auth_logout():
    try:
        if os.path.exists(Config.CACHE_FILE):
            os.remove(Config.CACHE_FILE)

        global spotify_service
        if spotify_service:
            spotify_service._initialized = False
            spotify_service.sp = None
            spotify_service.user_info = None

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/status')
def api_status():
    return jsonify(get_spotify_service().get_status())


@app.route('/api/devices')
def api_devices():
    return jsonify({'devices': get_spotify_service().get_devices()})


@app.route('/api/search', methods=['POST'])
def api_search():
    query = request.json.get('query', '')
    if not query:
        return jsonify({'artists': []})
    return jsonify({'artists': get_spotify_service().search_artist(query)})


@app.route('/api/set-artist', methods=['POST'])
def api_set_artist():
    artist = request.json.get('artist', '')
    if not artist:
        return jsonify({'success': False, 'error': 'No artist provided'})
    get_spotify_service().set_target_artist(artist)
    return jsonify({'success': True, 'artist': artist})


@app.route('/api/lock-device', methods=['POST'])
def api_lock_device():
    device_id = request.json.get('device_id')
    svc = get_spotify_service()
    if device_id:
        svc.lock_device(device_id)
        return jsonify({'success': True, 'locked': True})
    else:
        svc.unlock_device()
        return jsonify({'success': True, 'locked': False})


@app.route('/api/play', methods=['POST'])
def api_play():
    success = get_spotify_service().start_playback()
    return jsonify({'success': success})


@app.route('/api/stop', methods=['POST'])
def api_stop():
    success = get_spotify_service().stop_playback()
    return jsonify({'success': success})


@app.route('/api/settings', methods=['POST'])
def api_settings():
    data = request.json
    svc = get_spotify_service()
    if 'autoplay_enabled' in data:
        svc.set_autoplay_enabled(data['autoplay_enabled'])
    if 'idle_minutes' in data:
        svc.set_idle_time(data['idle_minutes'])
    return jsonify({'success': True})


if __name__ == '__main__':
    logger.info("Starting W3GH Web Interface...")
    start_autoplay_thread()
    app.run(host='0.0.0.0', port=5000, debug=False)


start_autoplay_thread()
