"""Config settings for W3GH Spotify AutoPlayer"""
import json
import os

# Base directory - where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    CREDENTIALS_FILE = os.path.join(BASE_DIR, '.spotify_credentials.json')
    SETTINGS_FILE = os.path.join(BASE_DIR, 'spoty_config.json')
    CACHE_FILE = os.path.join(BASE_DIR, '.cache')

    SPOTIFY_SCOPE = 'user-read-playback-state user-modify-playback-state user-read-currently-playing'
    SPOTIFY_REDIRECT_URI = 'https://rammfire.com/spo/auth/callback'

    # Defaults
    IDLE_TIME_MINUTES = 30
    CHECK_INTERVAL_SECONDS = 60
    TARGET_ARTIST = 'Death'
    LOCKED_DEVICE_ID = None
    AUTOPLAY_ENABLED = True

    SPOTIFY_CLIENT_ID = None
    SPOTIFY_CLIENT_SECRET = None

    @staticmethod
    def _settings_path():
        return Config.SETTINGS_FILE

    @staticmethod
    def load_settings():
        defaults = {
            'idle_time_minutes': Config.IDLE_TIME_MINUTES,
            'check_interval_seconds': Config.CHECK_INTERVAL_SECONDS,
            'target_artist': Config.TARGET_ARTIST,
            'locked_device_id': Config.LOCKED_DEVICE_ID,
            'autoplay_enabled': Config.AUTOPLAY_ENABLED
        }

        path = Config._settings_path()
        if not os.path.exists(path):
            return defaults

        try:
            with open(path, 'r') as f:
                data = json.load(f)
        except Exception:
            return defaults

        settings = dict(defaults)
        if isinstance(data.get('idle_time_minutes'), int):
            settings['idle_time_minutes'] = data['idle_time_minutes']
        if isinstance(data.get('check_interval_seconds'), int):
            settings['check_interval_seconds'] = data['check_interval_seconds']
        if isinstance(data.get('target_artist'), str) and data['target_artist'].strip():
            settings['target_artist'] = data['target_artist'].strip()
        if data.get('locked_device_id'):
            settings['locked_device_id'] = data['locked_device_id']
        if isinstance(data.get('autoplay_enabled'), bool):
            settings['autoplay_enabled'] = data['autoplay_enabled']

        return settings

    @staticmethod
    def save_settings(settings):
        path = Config._settings_path()
        with open(path, 'w') as f:
            json.dump(settings, f, indent=2)

    @staticmethod
    def apply_settings():
        settings = Config.load_settings()
        Config.IDLE_TIME_MINUTES = int(settings['idle_time_minutes'])
        Config.CHECK_INTERVAL_SECONDS = int(settings['check_interval_seconds'])
        Config.TARGET_ARTIST = str(settings['target_artist'])
        Config.LOCKED_DEVICE_ID = settings.get('locked_device_id')
        Config.AUTOPLAY_ENABLED = bool(settings.get('autoplay_enabled', True))

    @staticmethod
    def load_credentials():
        if not os.path.exists(Config.CREDENTIALS_FILE):
            raise ValueError(f"{Config.CREDENTIALS_FILE} not found!")
        with open(Config.CREDENTIALS_FILE, 'r') as f:
            creds = json.load(f)
        return creds.get('client_id'), creds.get('client_secret')

    @staticmethod
    def save_credentials(client_id, client_secret):
        with open(Config.CREDENTIALS_FILE, 'w') as f:
            json.dump({'client_id': client_id, 'client_secret': client_secret}, f, indent=2)

    @staticmethod
    def get_client_id():
        client_id, _ = Config.load_credentials()
        return client_id

    @staticmethod
    def get_client_secret():
        _, client_secret = Config.load_credentials()
        return client_secret

    @staticmethod
    def validate():
        client_id, client_secret = Config.load_credentials()
        if not client_id or not client_secret:
            raise ValueError("Spotify credentials missing!")
        Config.SPOTIFY_CLIENT_ID = client_id
        Config.SPOTIFY_CLIENT_SECRET = client_secret
        return True


Config.apply_settings()
