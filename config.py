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
            raise ValueError(
                "SPOTIFY_CLIENT_ID tanımlanmamış!\n"
                "1. .env dosyasını oluşturun: cp .env.example .env\n"
                "2. https://developer.spotify.com/dashboard adresine gidin\n"
                "3. 'Create app' ile uygulama oluşturun\n"
                "4. Client ID ve Client Secret'i .env dosyasına ekleyin"
            )
        if not Config.SPOTIFY_CLIENT_SECRET:
            raise ValueError(
                "SPOTIFY_CLIENT_SECRET tanımlanmamış!\n"
                "1. https://developer.spotify.com/dashboard adresine gidin\n"
                "2. Uygulamanızı açın\n"
                "3. 'Settings' > 'Basic Information' > 'Client Secret' (Show)\n"
                "4. Client Secret'i .env dosyasına ekleyin"
            )

        # Redirect URI kontrolü ve bilgilendirme
        if Config.SPOTIFY_REDIRECT_URI:
            print(f"\n{'='*60}")
            print(f"ℹ️  Redirect URI: {Config.SPOTIFY_REDIRECT_URI}")
            print(f"{'='*60}")
            print(f"Spotify Developer Dashboard'da bu URI'nin ekli olduğundan")
            print(f"emin olun:")
            print(f"1. https://developer.spotify.com/dashboard")
            print(f"2. Uygulamanızı seçin")
            print(f"3. 'Settings' > 'Redirect URIs'")
            print(f"4. Ekleyin: {Config.SPOTIFY_REDIRECT_URI}")
            print(f"5. 'Save' butonuna tıklayın")
            print(f"{'='*60}\n")

        return True
