#!/usr/bin/env python3
"""
Spotify OAuth - Manuel Authorization
Redirect URI olmadan çalışır, kullanıcı URL'yi kopyalar-yapıştırır
"""
import os
from spotipy.oauth2 import SpotifyOAuth
from config import Config


def manual_auth():
    """Manuel authorization flow"""
    Config.validate()

    print("\n" + "=" * 70)
    print("SPOTIFY OAUTH - MANUEL YETKİLENDİRME")
    print("=" * 70)
    print("\nBu yöntem redirect URI gerektirmez!")
    print("URL'yi kopyalayıp yapıştırmanız yeterli.\n")

    # Dummy redirect URI kullan
    redirect_uri = "http://example.com/callback"

    print(f"Redirect URI (dummy): {redirect_uri}")
    print("\nÖNEMLİ: Spotify Dashboard'da bu URI'yi eklemeniz GEREKLİ DEĞİL!")
    print("Sadece authorization code'u kopyalayacaksınız.\n")

    auth_manager = SpotifyOAuth(
        client_id=Config.SPOTIFY_CLIENT_ID,
        client_secret=Config.SPOTIFY_CLIENT_SECRET,
        redirect_uri=redirect_uri,
        scope=Config.SPOTIFY_SCOPE,
        cache_path='.cache',
        open_browser=True
    )

    # Get auth URL
    auth_url = auth_manager.get_authorize_url()

    print("=" * 70)
    print("ADIMLAR:")
    print("=" * 70)
    print("\n1. Tarayıcınızda şu URL açılacak (otomatik):")
    print(f"   {auth_url[:80]}...")
    print("\n2. Spotify ile giriş yapın")
    print("\n3. 'Agree' butonuna tıklayın")
    print("\n4. Hata sayfası açılacak (NORMAL! Endişe etmeyin)")
    print("   Sayfa yüklenemez hatası göreceksiniz")
    print("\n5. Tarayıcının adres çubuğundaki URL'in TAMAMINI kopyalayın")
    print("   Şuna benzer:")
    print("   http://example.com/callback?code=AQC5x...")
    print("\n6. Aşağıya yapıştırın")
    print("=" * 70)
    print()

    # Prompt for URL
    response_url = input("Yönlendirilen URL'i buraya yapıştırın: ").strip()

    if not response_url:
        print("\n❌ URL boş olamaz!")
        return None

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
        print("Artık uygulamayı normal şekilde kullanabilirsiniz:")
        print("  ./start.sh")
        print("\nveya:")
        print("  python spotify_autoplay.py")
        print()

        return token_info

    except Exception as e:
        print(f"\n❌ Hata: {e}")
        print("\nURL'yi doğru kopyaladığınızdan emin olun.")
        print("Tam URL gerekli: http://example.com/callback?code=...")
        return None


if __name__ == "__main__":
    manual_auth()
