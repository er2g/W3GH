"""Spotify Service - Core functionality for W3GH"""
import logging
import random
import time
from datetime import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import Config

logger = logging.getLogger(__name__)


class SpotifyService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.sp = None
        self.user_info = None

        self.autoplay_mode = False
        self.playback_stopped_time = None
        self.target_albums = []
        self.target_artist_id = None

    def connect(self):
        try:
            client_id = Config.get_client_id()
            client_secret = Config.get_client_secret()
        except Exception as e:
            logger.error(f"Credentials error: {e}")
            return False

        try:
            auth_manager = SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=Config.SPOTIFY_REDIRECT_URI,
                scope=Config.SPOTIFY_SCOPE,
                open_browser=False,
                cache_path=Config.CACHE_FILE
            )
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            self.user_info = self.sp.current_user()
            logger.info(f"Connected: {self.user_info['display_name']}")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    def is_connected(self):
        return self.sp is not None and self.user_info is not None

    def get_status(self):
        if not self.is_connected():
            return {'connected': False}

        playback = self.get_current_playback()
        settings = Config.load_settings()

        stopped_minutes = None
        if self.playback_stopped_time:
            stopped_minutes = (datetime.now() - self.playback_stopped_time).total_seconds() / 60

        return {
            'connected': True,
            'user': self.user_info.get('display_name', 'Unknown'),
            'is_premium': self.user_info.get('product') == 'premium',
            'autoplay_mode': self.autoplay_mode,
            'autoplay_enabled': settings.get('autoplay_enabled', True),
            'target_artist': settings.get('target_artist', 'Death'),
            'idle_minutes': settings.get('idle_time_minutes', 5),
            'locked_device_id': settings.get('locked_device_id'),
            'stopped_since_minutes': round(stopped_minutes, 1) if stopped_minutes else None,
            'playback': self._format_playback(playback),
            'devices': self.get_devices()
        }

    def _format_playback(self, playback):
        if not playback or not playback.get('item'):
            return None
        return {
            'track': playback['item']['name'],
            'artist': playback['item']['artists'][0]['name'],
            'album': playback['item']['album']['name'],
            'is_playing': playback.get('is_playing', False),
            'device': playback.get('device', {}).get('name', 'Unknown'),
            'device_id': playback.get('device', {}).get('id')
        }

    def get_devices(self):
        if not self.is_connected():
            return []
        try:
            result = self.sp.devices()
            return [{
                'id': d['id'],
                'name': d['name'],
                'type': d['type'],
                'is_active': d['is_active']
            } for d in result.get('devices', [])]
        except Exception as e:
            logger.error(f"Get devices error: {e}")
            return []

    def get_current_playback(self, raise_error=False):
        if not self.is_connected():
            return None
        try:
            return self.sp.current_playback()
        except Exception as e:
            logger.error(f"Playback error: {e}")
            if raise_error:
                raise e
            return None

    def search_artist(self, query):
        if not self.is_connected():
            return []
        try:
            results = self.sp.search(q=f"artist:{query}", type='artist', limit=10)
            return [{
                'id': a['id'],
                'name': a['name'],
                'image': a['images'][0]['url'] if a.get('images') else None,
                'followers': a.get('followers', {}).get('total', 0)
            } for a in results['artists']['items']]
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    def find_artist_and_albums(self, artist_name):
        if not self.is_connected():
            return None, []

        try:
            results = self.sp.search(q=f"artist:{artist_name}", type='artist', limit=20)

            target_artist = None
            for a in results['artists']['items']:
                if a['name'].lower() == artist_name.lower():
                    target_artist = a
                    break

            if not target_artist:
                logger.error(f"Artist '{artist_name}' not found!")
                return None, []

            artist_id = target_artist['id']
            logger.info(f"Found artist: {target_artist['name']} (ID: {artist_id})")

            albums_result = self.sp.artist_albums(artist_id, album_type='album', limit=50)

            valid_albums = []
            for album in albums_result['items']:
                album_artists = album.get('artists', [])
                if album_artists and album_artists[0]['id'] == artist_id:
                    album_name_lower = album['name'].lower()
                    # Skip compilations, live albums, reissues
                    skip_keywords = ['various', 'compilation', 'collection', 'best of', 'greatest hits',
                                     'classics', 'live', 'non:analog', 'on:stage', 'deluxe', 'reissue', 'remaster']
                    if not any(kw in album_name_lower for kw in skip_keywords):
                        valid_albums.append({
                            'uri': album['uri'],
                            'name': album['name'],
                            'id': album['id']
                        })

            seen_names = set()
            unique_albums = []
            for album in valid_albums:
                base_name = album['name'].split('(')[0].strip().lower()
                if base_name not in seen_names:
                    seen_names.add(base_name)
                    unique_albums.append(album)

            self.target_albums = unique_albums
            self.target_artist_id = artist_id

            logger.info(f"Found {len(unique_albums)} albums for {artist_name}")
            return artist_id, unique_albums

        except Exception as e:
            logger.error(f"Find artist/albums error: {e}")
            return None, []

    def get_locked_device_id(self):
        settings = Config.load_settings()
        return settings.get('locked_device_id')

    def start_playback_on_locked_device(self, artist_name=None):
        if not self.is_connected():
            return False

        settings = Config.load_settings()
        locked_device_id = settings.get('locked_device_id')

        if not locked_device_id:
            logger.error("No locked device!")
            return False

        devices = self.get_devices()
        device_available = any(d['id'] == locked_device_id for d in devices)

        if not device_available:
            logger.error("Locked device not available!")
            return False

        artist = artist_name or settings.get('target_artist', 'Death')
        artist_id, albums = self.find_artist_and_albums(artist)

        if not albums:
            logger.error(f"No albums for {artist}")
            return False

        try:
            random_album = random.choice(albums)
            logger.info(f"Selected: {random_album['name']}")

            # Start playback
            self.sp.start_playback(device_id=locked_device_id, context_uri=random_album['uri'])
            logger.info("Playback started")

            # Wait a bit for Spotify to register the playback
            time.sleep(2)

            # Set SHUFFLE ON (with retries)
            for _ in range(3):
                try:
                    self.sp.shuffle(True, device_id=locked_device_id)
                    logger.info("Shuffle: ON")
                    break
                except Exception as e:
                    logger.warning(f"Shuffle failed, retrying... {e}")
                    time.sleep(1)

            # Set REPEAT to context (album loop) (with retries)
            for _ in range(3):
                try:
                    self.sp.repeat('context', device_id=locked_device_id)
                    logger.info("Repeat: CONTEXT (album loop)")
                    break
                except Exception as e:
                    logger.warning(f"Repeat failed, retrying... {e}")
                    time.sleep(1)

            # Skip to next track to activate shuffle
            time.sleep(1)
            try:
                self.sp.next_track(device_id=locked_device_id)
                logger.info("Skipped to next track (shuffle activation)")
            except Exception as e:
                logger.error(f"Skip failed: {e}")

            self.autoplay_mode = True
            self.playback_stopped_time = None

            logger.info(f"NOW PLAYING: {artist} - {random_album['name']}")
            return True

        except Exception as e:
            logger.error(f"Start playback error: {e}")
            return False

    def start_playback(self, artist_name=None):
        return self.start_playback_on_locked_device(artist_name)

    def stop_playback(self):
        if not self.is_connected():
            return False
        try:
            self.sp.pause_playback()
            self.autoplay_mode = False
            return True
        except Exception as e:
            logger.error(f"Stop error: {e}")
            return False

    def stop_playback_on_locked_device(self):
        if not self.is_connected():
            return False

        locked_device_id = self.get_locked_device_id()
        if not locked_device_id:
            return False

        try:
            self.sp.pause_playback(device_id=locked_device_id)
            self.autoplay_mode = False
            logger.info("Stopped on locked device")
            return True
        except Exception as e:
            logger.error(f"Stop error: {e}")
            return False

    def set_target_artist(self, artist_name):
        settings = Config.load_settings()
        settings['target_artist'] = artist_name
        Config.save_settings(settings)
        Config.apply_settings()
        self.target_albums = []
        self.target_artist_id = None
        return True

    def lock_device(self, device_id):
        settings = Config.load_settings()
        settings['locked_device_id'] = device_id
        Config.save_settings(settings)
        Config.apply_settings()
        return True

    def unlock_device(self):
        settings = Config.load_settings()
        settings['locked_device_id'] = None
        Config.save_settings(settings)
        Config.apply_settings()
        return True

    def set_autoplay_enabled(self, enabled):
        settings = Config.load_settings()
        settings['autoplay_enabled'] = enabled
        Config.save_settings(settings)
        Config.apply_settings()
        return True

    def set_idle_time(self, minutes):
        settings = Config.load_settings()
        settings['idle_time_minutes'] = max(1, min(120, int(minutes)))
        Config.save_settings(settings)
        Config.apply_settings()
        return True

    def _is_target_artist_playing(self, playback):
        if not playback or not playback.get('item'):
            return False
        settings = Config.load_settings()
        target = settings.get('target_artist', 'Death').lower()
        for artist in playback['item'].get('artists', []):
            if artist['name'].lower() == target:
                return True
        return False

    def check_and_autoplay(self):
        if not self.is_connected():
            return

        settings = Config.load_settings()

        if not settings.get('autoplay_enabled', True):
            return

        locked_device_id = settings.get('locked_device_id')
        if not locked_device_id:
            return

        idle_time_minutes = settings.get('idle_time_minutes', 5)
        try:
            playback = self.get_current_playback(raise_error=True)
        except Exception as e:
            logger.error(f"Skipping check due to API error: {e}")
            return

        is_playing = False
        current_device_id = None

        if playback:
            is_playing = playback.get('is_playing', False)
            device_info = playback.get('device', {})
            current_device_id = device_info.get('id')

        if is_playing:
            self.playback_stopped_time = None

            if current_device_id == locked_device_id:
                if self._is_target_artist_playing(playback):
                    self.autoplay_mode = True
                    # Check if song is stuck at the end and skip
                    if playback.get('item'):
                        progress_ms = playback.get('progress_ms', 0)
                        duration_ms = playback['item'].get('duration_ms', 0)
                        # Increased window to 5000ms to be more robust
                        if duration_ms > 0 and progress_ms >= duration_ms - 5000:
                            logger.info("Song stuck at end, skipping...")
                            try:
                                self.sp.next_track(device_id=locked_device_id)
                            except Exception as e:
                                logger.error(f"Skip failed: {e}")
                else:
                    self.autoplay_mode = False
                    logger.info("User changed song, autoplay off")
            else:
                if self.autoplay_mode:
                    logger.info("User playing elsewhere, stopping locked device")
                    self.stop_playback_on_locked_device()
                    self.autoplay_mode = False
        else:
            # If playback is explicitly stopped, we reset autoplay_mode
            # so that it can restart after idle time.
            if self.autoplay_mode:
                logger.info("Playback stopped while in autoplay mode. Resetting mode to allow restart.")
                self.autoplay_mode = False

            if self.playback_stopped_time is None:
                self.playback_stopped_time = datetime.now()
                logger.info("Stopped, countdown...")

            stopped_minutes = (datetime.now() - self.playback_stopped_time).total_seconds() / 60

            if stopped_minutes >= idle_time_minutes and not self.autoplay_mode:
                logger.info(f"Idle {stopped_minutes:.1f} min -> AUTOPLAY!")
                if self.start_playback_on_locked_device():
                    self.playback_stopped_time = None


spotify_service = SpotifyService()
