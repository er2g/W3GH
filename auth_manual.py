#!/usr/bin/env python3
"""
Spotify OAuth - Basit Manuel Authorization
Credentials'ları sorar, .env'e yazar, token alır
"""
import os
import sys


def get_spotify_credentials():
    """Spotify credentials'ları al"""
    print("\n" + "=" * 70)
    print("SPOTIFY API KURULUMU")
    print("=" * 70)
    print("\n1. Adımlar:")
    print("   a) https://developer.spotify.com/dashboard adresine gidin")
    print("   b) 'Create app' ile uygulama oluşturun")
    print("   c) Client ID ve Client Secret'i kopyalayın")
    print("\n   NOT: Redirect URI eklemenize gerek YOK!\n")

    # Client ID
    client_id = input("Spotify Client ID: ").strip()
    if not client_id:
        print("❌ Client ID boş olamaz!")
        sys.exit(1)

    # Client Secret
    client_secret = input("Spotify Client Secret: ").strip()
    if not client_secret:
        print("❌ Client Secret boş olamaz!")
        sys.exit(1)

    return client_id, client_secret


def save_to_env(client_id, client_secret):
    """Credentials'ları .env dosyasına kaydet"""
    env_content = f"""# Spotify API Credentials
SPOTIFY_CLIENT_ID={client_id}
SPOTIFY_CLIENT_SECRET={client_secret}
SPOTIFY_REDIRECT_URI=http://example.com/callback

# Kullanıcı ayarları
IDLE_TIME_MINUTES=30
CHECK_INTERVAL_SECONDS=60
"""

    with open('.env', 'w') as f:
        f.write(env_content)

    print("\n✅ Credentials .env dosyasına kaydedildi")


def get_spotify_token():
    """Spotify token al"""
    try:
        from spotipy.oauth2 import SpotifyOAuth
    except ImportError:
        print("\n❌ spotipy kurulu değil!")
        print("Kurmak için: pip3 install spotipy python-dotenv")
        sys.exit(1)

    # .env'i yükle
    from dotenv import load_dotenv
    load_dotenv()

    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    redirect_uri = "http://example.com/callback"
    scope = 'user-read-playback-state user-modify-playback-state user-read-currently-playing'

    print("\n" + "=" * 70)
    print("SPOTIFY OAUTH")
    print("=" * 70)

    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope,
        cache_path='.cache',
        open_browser=True
    )

    # Get auth URL
    auth_url = auth_manager.get_authorize_url()

    print("\nAdımlar:")
    print("1. Tarayıcıda Spotify login açılacak")
    print("2. Giriş yapın ve 'Agree' tıklayın")
    print("3. Hata sayfası açılacak (NORMAL! Endişe etmeyin)")
    print("4. Adres çubuğundaki URL'in TAMAMINI kopyalayın")
    print("   Örnek: http://example.com/callback?code=AQC5x...")
    print()

    # Prompt for URL
    response_url = input("URL'i buraya yapıştırın: ").strip()

    if not response_url:
        print("\n❌ URL boş olamaz!")
        return False

    # Parse code from URL
    try:
        code = auth_manager.parse_response_code(response_url)
        token_info = auth_manager.get_access_token(code, as_dict=True, check_cache=False)

        # Save to cache
        auth_manager._save_token_info(token_info)

        print("\n" + "=" * 70)
        print("✅ BAŞARILI!")
        print("=" * 70)
        print(f"\nToken kaydedildi: .cache")
        print("\nArtık uygulamayı başlatabilirsiniz:")
        print("  python3 spotify_autoplay.py")
        print("\nveya:")
        print("  ./start.sh")
        print()

        return True

    except Exception as e:
        print(f"\n❌ Hata: {e}")
        print("\nURL'yi tam kopyaladığınızdan emin olun.")
        return False


def main():
    """Ana fonksiyon"""
    # .env var mı kontrol et
    if os.path.exists('.env'):
        print("\n✅ .env dosyası mevcut")
        choice = input("Yeniden oluşturmak ister misiniz? [e/h]: ").strip().lower()
        if choice != 'e':
            print("\nMevcut .env kullanılıyor...")
        else:
            # Credentials al ve kaydet
            client_id, client_secret = get_spotify_credentials()
            save_to_env(client_id, client_secret)
    else:
        # Credentials al ve kaydet
        client_id, client_secret = get_spotify_credentials()
        save_to_env(client_id, client_secret)

    # Token al
    if get_spotify_token():
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nİptal edildi.")
        sys.exit(1)
