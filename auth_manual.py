#!/usr/bin/env python3
"""
Spotify OAuth - Basit Manuel Authorization
Credentials'ları sorar, kaydeder, token alır
"""
import sys
from config import Config


def get_spotify_credentials():
    """Spotify credentials'ları al"""
    print("\n" + "=" * 70)
    print("SPOTIFY API KURULUMU")
    print("=" * 70)
    print("\nAdımlar:")
    print("  1. https://developer.spotify.com/dashboard")
    print("  2. 'Create app' ile uygulama oluşturun")
    print("  3. Client ID ve Client Secret'i kopyalayın")
    print("\n  NOT: Redirect URI eklemenize gerek YOK!\n")

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


def get_spotify_token(client_id, client_secret):
    """Spotify token al"""
    try:
        from spotipy.oauth2 import SpotifyOAuth
    except ImportError:
        print("\n❌ spotipy kurulu değil!")
        print("Kurmak için: pip3 install spotipy")
        sys.exit(1)

    redirect_uri = Config.SPOTIFY_REDIRECT_URI
    scope = Config.SPOTIFY_SCOPE

    print("\n" + "=" * 70)
    print("SPOTIFY OAUTH")
    print("=" * 70)
    print(f"\nRedirect URI: {redirect_uri}")
    print("(Dummy URL - Dashboard'a eklemenize gerek YOK!)")

    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope,
        cache_path='.cache',
        open_browser=True
    )

    print("\nAdımlar:")
    print("1. Tarayıcıda Spotify login açılacak")
    print("2. Giriş yapın ve 'Agree' tıklayın")
    print("3. Hata sayfası açılacak (NORMAL! Endişe etmeyin)")
    print("4. Adres çubuğundaki URL'in TAMAMINI kopyalayın")
    print(f"   Örnek: {redirect_uri}?code=AQC5x...")
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
        print(f"Credentials kaydedildi: {Config.CREDENTIALS_FILE}")
        print("\nArtık uygulamayı başlatabilirsiniz:")
        print("  python3 app.py")
        print()

        return True

    except Exception as e:
        print(f"\n❌ Hata: {e}")
        print("\nURL'yi tam kopyaladığınızdan emin olun.")
        print(f"Format: {redirect_uri}?code=...")
        return False


def main():
    """Ana fonksiyon"""
    # Credentials al
    client_id, client_secret = get_spotify_credentials()

    # Kaydet
    Config.save_credentials(client_id, client_secret)
    print(f"\n✅ Credentials kaydedildi: {Config.CREDENTIALS_FILE}")

    # Token al
    if get_spotify_token(client_id, client_secret):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nİptal edildi.")
        sys.exit(1)
