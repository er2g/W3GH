#!/usr/bin/env python3
"""
Spotify Web Yönetim Paneli
Tüm Spotify ayarlarını web üzerinden yönetin.
"""
import os
import json
import time
import threading
import logging
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('web_panel.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Konfigürasyon dosyaları
CREDENTIALS_FILE = '.spotify_credentials.json'
SETTINGS_FILE = '.spotify_settings.json'
CACHE_FILE = '.cache'

# Global değişkenler
spotify_player = None
player_thread = None
player_running = False


def get_default_settings():
    """Varsayılan ayarlar"""
    return {
        'idle_time_minutes': 30,
        'check_interval_seconds': 60,
        'artist_name': 'Death',
        'locked_device_id': None,
        'locked_device_name': None,
        'device_lock_enabled': False,
        'auto_start_on_boot': True,
        'shuffle_enabled': False,
        'repeat_mode': 'context',
        'volume_level': 50,
        'play_on_startup': True,
        'pause_on_device_lost': True,
        'custom_playlist_uri': None,
        'custom_playlist_name': None,
        'use_custom_playlist': False
    }


def load_settings():
    """Ayarları yükle"""
    defaults = get_default_settings()
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                saved = json.load(f)
                defaults.update(saved)
        except Exception as e:
            logger.error(f"Ayarlar yüklenirken hata: {e}")
    return defaults


def save_settings(settings):
    """Ayarları kaydet"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, indent=2, fp=f)
        return True
    except Exception as e:
        logger.error(f"Ayarlar kaydedilirken hata: {e}")
        return False


def load_credentials():
    """Spotify credentials yükle"""
    if os.path.exists(CREDENTIALS_FILE):
        try:
            with open(CREDENTIALS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return None


def save_credentials(client_id, client_secret):
    """Spotify credentials kaydet"""
    try:
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump({'client_id': client_id, 'client_secret': client_secret}, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Credentials kaydedilirken hata: {e}")
        return False


def get_spotify_oauth():
    """Spotify OAuth manager oluştur"""
    creds = load_credentials()
    if not creds:
        return None

    # Web tabanlı redirect URI
    redirect_uri = request.url_root.rstrip('/') + '/callback'

    return SpotifyOAuth(
        client_id=creds['client_id'],
        client_secret=creds['client_secret'],
        redirect_uri=redirect_uri,
        scope='user-read-playback-state user-modify-playback-state user-read-currently-playing user-library-read playlist-read-private playlist-read-collaborative user-read-private',
        cache_path=CACHE_FILE,
        show_dialog=True
    )


def get_spotify_client():
    """Spotify client al"""
    if not os.path.exists(CACHE_FILE):
        return None

    try:
        oauth = get_spotify_oauth()
        if oauth:
            token_info = oauth.get_cached_token()
            if token_info:
                return spotipy.Spotify(auth=token_info['access_token'])
    except Exception as e:
        logger.error(f"Spotify client hatası: {e}")
    return None


def spotify_required(f):
    """Spotify authentication kontrolü decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        sp = get_spotify_client()
        if not sp:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# =====================================================
# WEB ROUTES
# =====================================================

@app.route('/')
def index():
    """Ana sayfa"""
    creds = load_credentials()
    sp = get_spotify_client()
    settings = load_settings()

    user_info = None
    if sp:
        try:
            user_info = sp.current_user()
        except:
            pass

    return render_template('index.html',
                         has_credentials=creds is not None,
                         is_authenticated=sp is not None,
                         user_info=user_info,
                         settings=settings,
                         player_running=player_running)


@app.route('/setup', methods=['GET', 'POST'])
def setup():
    """Spotify API kurulum sayfası"""
    if request.method == 'POST':
        client_id = request.form.get('client_id', '').strip()
        client_secret = request.form.get('client_secret', '').strip()

        if client_id and client_secret:
            if save_credentials(client_id, client_secret):
                flash('API bilgileri kaydedildi! Şimdi Spotify hesabınızla giriş yapın.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Kaydetme hatası!', 'error')
        else:
            flash('Tüm alanları doldurun!', 'error')

    creds = load_credentials()
    return render_template('setup.html', credentials=creds)


@app.route('/login')
def login():
    """Spotify OAuth login"""
    creds = load_credentials()
    if not creds:
        flash('Önce API bilgilerini girin!', 'error')
        return redirect(url_for('setup'))

    oauth = get_spotify_oauth()
    auth_url = oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/callback')
def callback():
    """Spotify OAuth callback"""
    error = request.args.get('error')
    if error:
        flash(f'Spotify hatası: {error}', 'error')
        return redirect(url_for('index'))

    code = request.args.get('code')
    if not code:
        flash('Yetkilendirme kodu alınamadı!', 'error')
        return redirect(url_for('index'))

    try:
        oauth = get_spotify_oauth()
        token_info = oauth.get_access_token(code)

        if token_info:
            flash('Spotify hesabı başarıyla bağlandı!', 'success')
            return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f'Token hatası: {str(e)}', 'error')

    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    """Çıkış yap"""
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
    flash('Çıkış yapıldı.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@spotify_required
def dashboard():
    """Kontrol paneli"""
    sp = get_spotify_client()
    settings = load_settings()

    user_info = sp.current_user()
    playback = None
    devices = []

    try:
        playback = sp.current_playback()
        devices_response = sp.devices()
        devices = devices_response.get('devices', [])
    except Exception as e:
        logger.error(f"Dashboard veri hatası: {e}")

    return render_template('dashboard.html',
                         user_info=user_info,
                         playback=playback,
                         devices=devices,
                         settings=settings,
                         player_running=player_running)


@app.route('/devices')
@spotify_required
def devices_page():
    """Cihaz yönetimi sayfası"""
    sp = get_spotify_client()
    settings = load_settings()

    devices = []
    try:
        devices_response = sp.devices()
        devices = devices_response.get('devices', [])
    except Exception as e:
        logger.error(f"Cihaz listesi hatası: {e}")

    return render_template('devices.html',
                         devices=devices,
                         settings=settings)


@app.route('/playlists')
@spotify_required
def playlists_page():
    """Playlist yönetimi sayfası"""
    sp = get_spotify_client()
    settings = load_settings()

    playlists = []
    try:
        results = sp.current_user_playlists(limit=50)
        playlists = results.get('items', [])
    except Exception as e:
        logger.error(f"Playlist listesi hatası: {e}")

    # Artist albümlerini de al
    artist_albums = []
    try:
        artist_name = settings.get('artist_name', 'Death')
        results = sp.search(q=f'artist:{artist_name}', type='artist', limit=5)
        for artist in results['artists']['items']:
            if artist['name'].lower() == artist_name.lower():
                albums = sp.artist_albums(artist['id'], album_type='album', limit=50)
                artist_albums = albums.get('items', [])
                break
    except Exception as e:
        logger.error(f"Artist albümleri hatası: {e}")

    return render_template('playlists.html',
                         playlists=playlists,
                         artist_albums=artist_albums,
                         settings=settings)


@app.route('/settings', methods=['GET', 'POST'])
@spotify_required
def settings_page():
    """Ayarlar sayfası"""
    if request.method == 'POST':
        settings = load_settings()

        # Form verilerini al
        settings['idle_time_minutes'] = int(request.form.get('idle_time_minutes', 30))
        settings['check_interval_seconds'] = int(request.form.get('check_interval_seconds', 60))
        settings['artist_name'] = request.form.get('artist_name', 'Death')
        settings['shuffle_enabled'] = request.form.get('shuffle_enabled') == 'on'
        settings['repeat_mode'] = request.form.get('repeat_mode', 'context')
        settings['volume_level'] = int(request.form.get('volume_level', 50))
        settings['play_on_startup'] = request.form.get('play_on_startup') == 'on'
        settings['pause_on_device_lost'] = request.form.get('pause_on_device_lost') == 'on'
        settings['auto_start_on_boot'] = request.form.get('auto_start_on_boot') == 'on'

        if save_settings(settings):
            flash('Ayarlar kaydedildi!', 'success')
        else:
            flash('Ayarlar kaydedilemedi!', 'error')

        return redirect(url_for('settings_page'))

    settings = load_settings()
    return render_template('settings.html', settings=settings)


@app.route('/logs')
@spotify_required
def logs_page():
    """Log izleme sayfası"""
    logs = []
    log_files = ['web_panel.log', 'spotify_autoplay.log', 'service.log']

    for log_file in log_files:
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()[-100:]  # Son 100 satır
                    logs.append({
                        'file': log_file,
                        'lines': lines
                    })
            except Exception as e:
                logger.error(f"Log okuma hatası ({log_file}): {e}")

    return render_template('logs.html', logs=logs)


# =====================================================
# API ENDPOINTS
# =====================================================

@app.route('/api/status')
def api_status():
    """Sistem durumu API"""
    sp = get_spotify_client()
    settings = load_settings()

    status = {
        'authenticated': sp is not None,
        'player_running': player_running,
        'settings': settings,
        'playback': None,
        'devices': [],
        'locked_device_online': False
    }

    if sp:
        try:
            status['playback'] = sp.current_playback()
            devices_response = sp.devices()
            status['devices'] = devices_response.get('devices', [])

            # Kilitli cihaz kontrolü
            if settings.get('device_lock_enabled') and settings.get('locked_device_id'):
                for device in status['devices']:
                    if device['id'] == settings['locked_device_id']:
                        status['locked_device_online'] = True
                        break
        except Exception as e:
            status['error'] = str(e)

    return jsonify(status)


@app.route('/api/devices')
@spotify_required
def api_devices():
    """Cihaz listesi API"""
    sp = get_spotify_client()
    try:
        devices = sp.devices()
        return jsonify(devices)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/devices/lock', methods=['POST'])
@spotify_required
def api_lock_device():
    """Cihaz kilitle"""
    data = request.json
    device_id = data.get('device_id')
    device_name = data.get('device_name')

    settings = load_settings()
    settings['locked_device_id'] = device_id
    settings['locked_device_name'] = device_name
    settings['device_lock_enabled'] = True

    if save_settings(settings):
        logger.info(f"Cihaz kilitlendi: {device_name} ({device_id})")
        return jsonify({'success': True, 'message': f'{device_name} cihazı kilitlendi'})

    return jsonify({'success': False, 'message': 'Kaydetme hatası'}), 500


@app.route('/api/devices/unlock', methods=['POST'])
@spotify_required
def api_unlock_device():
    """Cihaz kilidini kaldır"""
    settings = load_settings()
    settings['locked_device_id'] = None
    settings['locked_device_name'] = None
    settings['device_lock_enabled'] = False

    if save_settings(settings):
        logger.info("Cihaz kilidi kaldırıldı")
        return jsonify({'success': True, 'message': 'Cihaz kilidi kaldırıldı'})

    return jsonify({'success': False, 'message': 'Kaydetme hatası'}), 500


@app.route('/api/devices/transfer', methods=['POST'])
@spotify_required
def api_transfer_playback():
    """Çalmayı başka cihaza aktar"""
    sp = get_spotify_client()
    data = request.json
    device_id = data.get('device_id')

    try:
        sp.transfer_playback(device_id, force_play=True)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/playback/play', methods=['POST'])
@spotify_required
def api_play():
    """Çalmaya başla"""
    sp = get_spotify_client()
    settings = load_settings()
    data = request.json or {}

    device_id = data.get('device_id')
    context_uri = data.get('context_uri')

    # Kilitli cihaz kontrolü
    if settings.get('device_lock_enabled') and settings.get('locked_device_id'):
        device_id = settings['locked_device_id']

    try:
        if context_uri:
            sp.start_playback(device_id=device_id, context_uri=context_uri)
        else:
            sp.start_playback(device_id=device_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/playback/pause', methods=['POST'])
@spotify_required
def api_pause():
    """Durdur"""
    sp = get_spotify_client()
    try:
        sp.pause_playback()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/playback/next', methods=['POST'])
@spotify_required
def api_next():
    """Sonraki şarkı"""
    sp = get_spotify_client()
    try:
        sp.next_track()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/playback/previous', methods=['POST'])
@spotify_required
def api_previous():
    """Önceki şarkı"""
    sp = get_spotify_client()
    try:
        sp.previous_track()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/playback/volume', methods=['POST'])
@spotify_required
def api_volume():
    """Ses seviyesi ayarla"""
    sp = get_spotify_client()
    data = request.json
    volume = data.get('volume', 50)

    try:
        sp.volume(int(volume))

        # Ayarlara da kaydet
        settings = load_settings()
        settings['volume_level'] = int(volume)
        save_settings(settings)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/playback/shuffle', methods=['POST'])
@spotify_required
def api_shuffle():
    """Shuffle aç/kapat"""
    sp = get_spotify_client()
    data = request.json
    state = data.get('state', False)

    try:
        sp.shuffle(state)

        settings = load_settings()
        settings['shuffle_enabled'] = state
        save_settings(settings)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/playback/repeat', methods=['POST'])
@spotify_required
def api_repeat():
    """Repeat modu ayarla"""
    sp = get_spotify_client()
    data = request.json
    mode = data.get('mode', 'off')  # off, context, track

    try:
        sp.repeat(mode)

        settings = load_settings()
        settings['repeat_mode'] = mode
        save_settings(settings)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/playlist/set', methods=['POST'])
@spotify_required
def api_set_playlist():
    """Özel playlist ayarla"""
    data = request.json
    playlist_uri = data.get('uri')
    playlist_name = data.get('name')

    settings = load_settings()
    settings['custom_playlist_uri'] = playlist_uri
    settings['custom_playlist_name'] = playlist_name
    settings['use_custom_playlist'] = True

    if save_settings(settings):
        return jsonify({'success': True, 'message': f'{playlist_name} seçildi'})

    return jsonify({'success': False, 'message': 'Kaydetme hatası'}), 500


@app.route('/api/playlist/clear', methods=['POST'])
@spotify_required
def api_clear_playlist():
    """Özel playlist temizle"""
    settings = load_settings()
    settings['custom_playlist_uri'] = None
    settings['custom_playlist_name'] = None
    settings['use_custom_playlist'] = False

    if save_settings(settings):
        return jsonify({'success': True})

    return jsonify({'success': False}), 500


@app.route('/api/player/start', methods=['POST'])
@spotify_required
def api_start_player():
    """Otomatik player'ı başlat"""
    global spotify_player, player_thread, player_running

    if player_running:
        return jsonify({'success': False, 'message': 'Player zaten çalışıyor'})

    try:
        player_running = True
        player_thread = threading.Thread(target=run_player_loop, daemon=True)
        player_thread.start()
        logger.info("Player başlatıldı")
        return jsonify({'success': True, 'message': 'Player başlatıldı'})
    except Exception as e:
        player_running = False
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/player/stop', methods=['POST'])
@spotify_required
def api_stop_player():
    """Otomatik player'ı durdur"""
    global player_running

    player_running = False
    logger.info("Player durduruldu")
    return jsonify({'success': True, 'message': 'Player durduruldu'})


@app.route('/api/search/artist', methods=['GET'])
@spotify_required
def api_search_artist():
    """Artist ara"""
    sp = get_spotify_client()
    query = request.args.get('q', '')

    if not query:
        return jsonify({'artists': []})

    try:
        results = sp.search(q=f'artist:{query}', type='artist', limit=10)
        return jsonify({'artists': results['artists']['items']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/artist/albums', methods=['GET'])
@spotify_required
def api_artist_albums():
    """Artist albümlerini getir"""
    sp = get_spotify_client()
    artist_id = request.args.get('artist_id', '')

    if not artist_id:
        return jsonify({'albums': []})

    try:
        results = sp.artist_albums(artist_id, album_type='album', limit=50)
        return jsonify({'albums': results['items']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =====================================================
# PLAYER LOOP
# =====================================================

def run_player_loop():
    """Arka plan player döngüsü"""
    global player_running

    logger.info("Player döngüsü başlatılıyor...")

    last_activity_time = datetime.now()
    last_track_id = None
    last_is_playing = False
    autoplay_mode = False

    while player_running:
        try:
            sp = get_spotify_client()
            if not sp:
                logger.error("Spotify client yok, bekleniyor...")
                time.sleep(10)
                continue

            settings = load_settings()

            # Cihaz kilidi kontrolü
            if settings.get('device_lock_enabled') and settings.get('locked_device_id'):
                devices_response = sp.devices()
                devices = devices_response.get('devices', [])

                device_found = False
                for device in devices:
                    if device['id'] == settings['locked_device_id']:
                        device_found = True
                        break

                if not device_found and settings.get('pause_on_device_lost'):
                    logger.warning(f"Kilitli cihaz bulunamadı: {settings.get('locked_device_name')}")
                    if autoplay_mode:
                        try:
                            sp.pause_playback()
                            logger.info("Çalma duraklatıldı (cihaz kayıp)")
                        except:
                            pass
                        autoplay_mode = False
                    time.sleep(settings['check_interval_seconds'])
                    continue

            # Mevcut çalma durumu
            playback = sp.current_playback()

            if playback:
                current_track_id = playback.get('item', {}).get('id') if playback.get('item') else None
                is_playing = playback.get('is_playing', False)

                # Kullanıcı aktivitesi kontrolü
                user_activity = False

                if current_track_id and current_track_id != last_track_id:
                    if last_track_id is not None:
                        if not autoplay_mode:
                            user_activity = True
                            logger.info("Kullanıcı aktivitesi: Şarkı değişti")

                if is_playing != last_is_playing:
                    if not autoplay_mode:
                        user_activity = True
                        logger.info(f"Kullanıcı aktivitesi: {'Çalıyor' if is_playing else 'Duraklatıldı'}")

                last_track_id = current_track_id
                last_is_playing = is_playing

                if user_activity:
                    last_activity_time = datetime.now()
                    if autoplay_mode:
                        logger.info("Kullanıcı müdahalesi, otomatik mod kapatıldı")
                        autoplay_mode = False

            # Boşta kalma kontrolü
            idle_time = datetime.now() - last_activity_time
            idle_minutes = idle_time.total_seconds() / 60

            if not autoplay_mode and idle_minutes >= settings['idle_time_minutes']:
                logger.info(f"{idle_minutes:.1f} dakika boşta, otomatik çalma başlatılıyor...")

                # Cihaz seç
                device_id = settings.get('locked_device_id')
                if not device_id:
                    devices_response = sp.devices()
                    devices = devices_response.get('devices', [])
                    if devices:
                        for d in devices:
                            if d['is_active']:
                                device_id = d['id']
                                break
                        if not device_id:
                            device_id = devices[0]['id']

                if device_id:
                    # Ne çalacağını belirle
                    context_uri = None

                    if settings.get('use_custom_playlist') and settings.get('custom_playlist_uri'):
                        context_uri = settings['custom_playlist_uri']
                        logger.info(f"Playlist çalınıyor: {settings.get('custom_playlist_name')}")
                    else:
                        # Artist albümü bul
                        artist_name = settings.get('artist_name', 'Death')
                        results = sp.search(q=f'artist:{artist_name}', type='artist', limit=5)

                        for artist in results['artists']['items']:
                            if artist['name'].lower() == artist_name.lower():
                                albums = sp.artist_albums(artist['id'], album_type='album', limit=1)
                                if albums['items']:
                                    context_uri = albums['items'][0]['uri']
                                    logger.info(f"Artist albümü çalınıyor: {albums['items'][0]['name']}")
                                break

                    if context_uri:
                        try:
                            sp.start_playback(device_id=device_id, context_uri=context_uri)
                            sp.repeat(settings.get('repeat_mode', 'context'), device_id=device_id)
                            sp.shuffle(settings.get('shuffle_enabled', False), device_id=device_id)

                            if settings.get('volume_level'):
                                sp.volume(settings['volume_level'], device_id=device_id)

                            autoplay_mode = True
                            last_activity_time = datetime.now()
                            logger.info("Otomatik çalma başlatıldı!")
                        except Exception as e:
                            logger.error(f"Çalma hatası: {e}")

            time.sleep(settings['check_interval_seconds'])

        except Exception as e:
            logger.error(f"Player döngüsü hatası: {e}")
            time.sleep(10)

    logger.info("Player döngüsü durduruldu")


# =====================================================
# TEMPLATES
# =====================================================

# Template klasörünü oluştur
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)


if __name__ == '__main__':
    # Debug modunda çalıştır
    app.run(host='0.0.0.0', port=5000, debug=True)
