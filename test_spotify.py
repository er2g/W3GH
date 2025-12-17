#!/usr/bin/env python3
"""
Spotify bağlantı test scripti
"""
import sys
from config import Config
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def test_connection():
    """Spotify API bağlantısını test et"""
    print("=" * 50)
    print("Spotify Bağlantı Testi")
    print("=" * 50)
    print()

    # Config kontrolü
    print("[1/4] Konfigürasyon kontrolü...")
    try:
        Config.validate()
        print("✓ Konfigürasyon OK")
        print(f"  Client ID: {Config.SPOTIFY_CLIENT_ID[:10]}...")
        print(f"  Redirect URI: {Config.SPOTIFY_REDIRECT_URI}")
    except Exception as e:
        print(f"✗ Konfigürasyon hatası: {e}")
        return False

    # Spotify auth
    print()
    print("[2/4] Spotify kimlik doğrulama...")
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=Config.SPOTIFY_CLIENT_ID,
            client_secret=Config.SPOTIFY_CLIENT_SECRET,
            redirect_uri=Config.SPOTIFY_REDIRECT_URI,
            scope=Config.SPOTIFY_SCOPE
        ))
        print("✓ Kimlik doğrulama başarılı")
    except Exception as e:
        print(f"✗ Kimlik doğrulama hatası: {e}")
        return False

    # Kullanıcı bilgisi
    print()
    print("[3/4] Kullanıcı bilgisi alınıyor...")
    try:
        user = sp.current_user()
        print("✓ Kullanıcı bulundu")
        print(f"  İsim: {user['display_name']}")
        print(f"  ID: {user['id']}")
        print(f"  Premium: {'Evet' if user['product'] == 'premium' else 'Hayır'}")

        if user['product'] != 'premium':
            print()
            print("⚠️  UYARI: Spotify Premium hesap gereklidir!")
            print("   Playback kontrolü Premium hesaplarda çalışır.")
    except Exception as e:
        print(f"✗ Kullanıcı bilgisi alınamadı: {e}")
        return False

    # Aktif cihazlar
    print()
    print("[4/4] Aktif cihazlar kontrol ediliyor...")
    try:
        devices = sp.devices()
        if devices['devices']:
            print(f"✓ {len(devices['devices'])} aktif cihaz bulundu:")
            for device in devices['devices']:
                active = "🔊" if device['is_active'] else "  "
                print(f"  {active} {device['name']} ({device['type']})")
        else:
            print("⚠️  Aktif cihaz bulunamadı")
            print("   Spotify uygulamasını açın ve bir şarkı çalın.")
    except Exception as e:
        print(f"✗ Cihaz bilgisi alınamadı: {e}")
        return False

    # Death grubu testi
    print()
    print("[5/5] Death grubu aranıyor...")
    try:
        results = sp.search(q='artist:Death metal', type='artist', limit=10)
        death_artist = None
        for artist in results['artists']['items']:
            if artist['name'].lower() == 'death':
                death_artist = artist
                break

        if death_artist:
            print(f"✓ Death grubu bulundu")
            print(f"  Spotify ID: {death_artist['id']}")
            print(f"  Popülerlik: {death_artist['popularity']}/100")

            # Albümleri listele
            albums = sp.artist_albums(death_artist['id'], album_type='album', limit=10)
            print(f"  Albümler ({len(albums['items'])}):")
            for album in albums['items'][:5]:
                print(f"    - {album['name']} ({album['release_date'][:4]})")
        else:
            print("✗ Death grubu bulunamadı")
            return False
    except Exception as e:
        print(f"✗ Death arama hatası: {e}")
        return False

    print()
    print("=" * 50)
    print("✓ Tüm testler başarılı!")
    print("=" * 50)
    print()
    print("Sistemi başlatmak için:")
    print("  ./start.sh")
    print()
    print("veya")
    print()
    print("  sudo systemctl start spotify-autoplay@$USER.service")
    print()

    return True


if __name__ == "__main__":
    try:
        success = test_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest iptal edildi.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nBeklenmeyen hata: {e}")
        sys.exit(1)
