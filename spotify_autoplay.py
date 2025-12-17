#!/usr/bin/env python3
"""
Spotify Otomatik Çalma Sistemi
Death grubunun albümlerini otomatik olarak çalar.
"""
import time
import logging
from datetime import datetime, timedelta
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import Config

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('spotify_autoplay.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SpotifyAutoPlayer:
    def __init__(self):
        """Spotify otomatik çalma sınıfını başlat"""
        Config.validate()

        try:
            # Spotify OAuth kurulumu
            logger.info("Spotify kimlik doğrulama başlatılıyor...")

            auth_manager = SpotifyOAuth(
                client_id=Config.SPOTIFY_CLIENT_ID,
                client_secret=Config.SPOTIFY_CLIENT_SECRET,
                redirect_uri=Config.SPOTIFY_REDIRECT_URI,
                scope=Config.SPOTIFY_SCOPE,
                open_browser=True,  # Tarayıcıyı otomatik aç
                cache_path='.cache'  # Token cache dosyası
            )

            self.sp = spotipy.Spotify(auth_manager=auth_manager)

            # Test connection
            user = self.sp.current_user()
            logger.info(f"✓ Spotify'a bağlandı: {user['display_name']} ({user['id']})")

            if user['product'] != 'premium':
                logger.warning("⚠️  UYARI: Spotify Premium hesap gereklidir!")
                logger.warning("   Playback kontrolü Premium hesaplarda çalışır.")

        except Exception as e:
            logger.error(f"❌ Spotify kimlik doğrulama hatası: {e}")
            logger.error("\n" + "="*60)
            logger.error("Olası çözümler:")
            logger.error("1. Redirect URI'yi kontrol edin:")
            logger.error(f"   .env dosyası: {Config.SPOTIFY_REDIRECT_URI}")
            logger.error("   Spotify Dashboard'da AYNI URI ekli olmalı!")
            logger.error("")
            logger.error("2. Tarayıcıda yetkilendirme yapın:")
            logger.error("   - Spotify login sayfası açılacak")
            logger.error("   - Giriş yapın ve 'Agree' tıklayın")
            logger.error("   - Yönlendirme URL'ini kopyalayın")
            logger.error("   - Terminale yapıştırın")
            logger.error("")
            logger.error("3. .cache dosyasını silin ve tekrar deneyin:")
            logger.error("   rm .cache*")
            logger.error("")
            logger.error("4. Client ID ve Secret'i kontrol edin (.env dosyası)")
            logger.error("="*60 + "\n")
            raise

        self.last_activity_time = datetime.now()
        self.last_track_id = None
        self.last_is_playing = False
        self.autoplay_mode = False
        self.death_albums = []

        logger.info("Spotify AutoPlayer başlatıldı")
        self._find_death_albums()

    def _find_death_albums(self):
        """Death grubunun tüm albümlerini bul"""
        try:
            # Death grubunu ara
            results = self.sp.search(q='artist:Death metal', type='artist', limit=10)
            death_artist = None

            for artist in results['artists']['items']:
                if artist['name'].lower() == 'death':
                    death_artist = artist
                    break

            if not death_artist:
                logger.error("Death grubu bulunamadı!")
                return

            artist_id = death_artist['id']
            logger.info(f"Death grubu bulundu: {artist_id}")

            # Tüm albümleri al
            albums = self.sp.artist_albums(artist_id, album_type='album', limit=50)

            self.death_albums = []
            for album in albums['items']:
                self.death_albums.append({
                    'uri': album['uri'],
                    'name': album['name'],
                    'id': album['id']
                })

            logger.info(f"{len(self.death_albums)} adet Death albümü bulundu: {[a['name'] for a in self.death_albums]}")

        except Exception as e:
            logger.error(f"Death albümleri bulunurken hata: {e}")

    def get_current_playback(self):
        """Mevcut çalma durumunu al"""
        try:
            return self.sp.current_playback()
        except Exception as e:
            logger.error(f"Playback bilgisi alınırken hata: {e}")
            return None

    def check_user_activity(self):
        """Kullanıcı aktivitesini kontrol et"""
        playback = self.get_current_playback()

        if playback is None:
            # Oynatma durumu yok
            return False

        current_track_id = playback.get('item', {}).get('id') if playback.get('item') else None
        is_playing = playback.get('is_playing', False)

        # Kullanıcı aktivitesi kontrolü
        user_activity = False

        # 1. Şarkı değişti mi? (kullanıcı atladı)
        if current_track_id and current_track_id != self.last_track_id:
            if self.last_track_id is not None:  # İlk başlangıçta aktivite sayma
                # Otomatik mod değilse veya Death dışı bir şarkıya geçildiyse
                if not self.autoplay_mode or not self._is_death_track(playback):
                    user_activity = True
                    logger.info("Kullanıcı aktivitesi: Şarkı değiştirildi")

        # 2. Oynatma durumu değişti mi? (kullanıcı durdurdu/başlattı)
        if is_playing != self.last_is_playing:
            if not self.autoplay_mode:  # Otomatik moddaysak bu aktivite sayılmaz
                user_activity = True
                action = "başlattı" if is_playing else "durdurdu"
                logger.info(f"Kullanıcı aktivitesi: Çalmayı {action}")

        # Son durumu kaydet
        self.last_track_id = current_track_id
        self.last_is_playing = is_playing

        # Kullanıcı aktivitesi varsa zamanı güncelle
        if user_activity:
            self.last_activity_time = datetime.now()
            # Kullanıcı müdahale ettiğinde otomatik modu kapat
            if self.autoplay_mode:
                logger.info("Kullanıcı müdahale etti, otomatik mod kapatıldı")
                self.autoplay_mode = False

        return user_activity

    def _is_death_track(self, playback):
        """Çalan şarkının Death'e ait olup olmadığını kontrol et"""
        if not playback or not playback.get('item'):
            return False

        artists = playback['item'].get('artists', [])
        for artist in artists:
            if artist['name'].lower() == 'death':
                return True
        return False

    def start_death_playback(self):
        """Death albümlerini çalmaya başla"""
        if not self.death_albums:
            logger.error("Death albümü bulunamadı, çalma başlatılamıyor")
            return False

        try:
            # İlk albümü çal
            album_uri = self.death_albums[0]['uri']
            logger.info(f"Death çalınıyor: {self.death_albums[0]['name']}")

            # Aktif cihazı bul
            devices = self.sp.devices()
            if not devices['devices']:
                logger.error("Aktif Spotify cihazı bulunamadı!")
                return False

            device_id = devices['devices'][0]['id']

            # Albümü çal
            self.sp.start_playback(device_id=device_id, context_uri=album_uri)

            # Repeat modunu aç (tüm albümler için)
            self.sp.repeat('context', device_id=device_id)

            # Shuffle'ı kapat (albüm sırasıyla çalsın)
            self.sp.shuffle(False, device_id=device_id)

            self.autoplay_mode = True
            self.last_activity_time = datetime.now()

            logger.info("Otomatik çalma modu başlatıldı (Death albümleri loop'ta)")
            return True

        except Exception as e:
            logger.error(f"Death çalınırken hata: {e}")
            return False

    def run(self):
        """Ana döngü"""
        logger.info(f"İzleme başladı. Boşta kalma süresi: {Config.IDLE_TIME_MINUTES} dakika")
        logger.info(f"Kontrol aralığı: {Config.CHECK_INTERVAL_SECONDS} saniye")

        while True:
            try:
                # Kullanıcı aktivitesini kontrol et
                self.check_user_activity()

                # Boşta kalma süresini hesapla
                idle_time = datetime.now() - self.last_activity_time
                idle_minutes = idle_time.total_seconds() / 60

                # Otomatik mod kapalıysa ve boşta kalma süresi aşıldıysa
                if not self.autoplay_mode and idle_minutes >= Config.IDLE_TIME_MINUTES:
                    logger.info(f"{idle_minutes:.1f} dakika boşta, Death çalmaya başlıyorum...")
                    self.start_death_playback()

                # Otomatik moddaysa durumu logla
                if self.autoplay_mode:
                    playback = self.get_current_playback()
                    if playback and playback.get('item'):
                        track_name = playback['item']['name']
                        artist_name = playback['item']['artists'][0]['name']
                        logger.info(f"Otomatik mod: {artist_name} - {track_name}")

                # Bekle
                time.sleep(Config.CHECK_INTERVAL_SECONDS)

            except KeyboardInterrupt:
                logger.info("Program sonlandırılıyor...")
                break
            except Exception as e:
                logger.error(f"Beklenmeyen hata: {e}")
                time.sleep(Config.CHECK_INTERVAL_SECONDS)


def main():
    """Ana fonksiyon"""
    try:
        player = SpotifyAutoPlayer()
        player.run()
    except Exception as e:
        logger.error(f"Program başlatılırken hata: {e}")
        raise


if __name__ == "__main__":
    main()
