"""
Konfigürasyon ayarları
"""
import json
import os


class Config:
    # Credentials dosyası
    CREDENTIALS_FILE = '.spotify_credentials.json'

    # Spotify scope'ları
    SPOTIFY_SCOPE = 'user-read-playback-state user-modify-playback-state user-read-currently-playing'

    # Redirect URI - HTTPS dummy (Spotify zorunluluğu)
    SPOTIFY_REDIRECT_URI = 'https://example.com/callback'

    # Zamanlama ayarları
    IDLE_TIME_MINUTES = 30
    CHECK_INTERVAL_SECONDS = 60

    # Death grubu
    DEATH_ARTIST_NAME = "Death"

    @staticmethod
    def load_credentials():
        """Credentials dosyasından yükle"""
        if not os.path.exists(Config.CREDENTIALS_FILE):
            raise ValueError(
                f"{Config.CREDENTIALS_FILE} dosyası bulunamadı!\n\n"
                "Önce şunu çalıştırın:\n"
                "  python3 auth_manual.py\n"
            )

        with open(Config.CREDENTIALS_FILE, 'r') as f:
            creds = json.load(f)

        return creds.get('client_id'), creds.get('client_secret')

    @staticmethod
    def save_credentials(client_id, client_secret):
        """Credentials dosyasına kaydet"""
        creds = {
            'client_id': client_id,
            'client_secret': client_secret
        }

        with open(Config.CREDENTIALS_FILE, 'w') as f:
            json.dump(creds, f, indent=2)

    @staticmethod
    def get_client_id():
        """Client ID al"""
        client_id, _ = Config.load_credentials()
        return client_id

    @staticmethod
    def get_client_secret():
        """Client Secret al"""
        _, client_secret = Config.load_credentials()
        return client_secret
