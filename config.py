"""
Konfigürasyon ayarları
"""
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

class Config:
    # Spotify API bilgileri
    SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
    SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:8888/callback')

    # Zamanlama ayarları
    IDLE_TIME_MINUTES = int(os.getenv('IDLE_TIME_MINUTES', '30'))
    CHECK_INTERVAL_SECONDS = int(os.getenv('CHECK_INTERVAL_SECONDS', '60'))

    # Spotify scope'ları
    SPOTIFY_SCOPE = 'user-read-playback-state user-modify-playback-state user-read-currently-playing'

    # Death grubu (otomatik bulunacak)
    DEATH_ARTIST_URI = os.getenv('DEATH_ARTIST_URI', None)
    DEATH_ARTIST_NAME = "Death"

    @staticmethod
    def validate():
        """Gerekli konfigürasyonları kontrol et"""
        if not Config.SPOTIFY_CLIENT_ID:
            raise ValueError("SPOTIFY_CLIENT_ID tanımlanmamış. .env dosyasını kontrol edin.")
        if not Config.SPOTIFY_CLIENT_SECRET:
            raise ValueError("SPOTIFY_CLIENT_SECRET tanımlanmamış. .env dosyasını kontrol edin.")
        return True
