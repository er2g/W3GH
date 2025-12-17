#!/usr/bin/env python3
"""
Spotify OAuth - ngrok ile HTTPS Tunnel
HTTPS redirect URI için ngrok kullanır
"""
import os
import sys
import subprocess
import time
import signal
from spotipy.oauth2 import SpotifyOAuth
from config import Config


def check_ngrok():
    """ngrok kurulu mu kontrol et"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def install_ngrok():
    """ngrok kurulum talimatları"""
    print("\n" + "=" * 70)
    print("NGROK KURULUMU GEREKLİ")
    print("=" * 70)
    print("""
ngrok, localhost'unuzu internete açan bir tunnel servisidir.
HTTPS URL sağlar, böylece Spotify API ile çalışabilirsiniz.

KURULUM:

Ubuntu/Debian:
  curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | \
    sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
  echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | \
    sudo tee /etc/apt/sources.list.d/ngrok.list
  sudo apt update
  sudo apt install ngrok

Manuel indirme:
  1. https://ngrok.com/download adresine gidin
  2. Linux versiyonunu indirin
  3. Çıkartıp /usr/local/bin/ klasörüne kopyalayın

Snap ile:
  sudo snap install ngrok

Test:
  ngrok version
""")
    choice = input("Şimdi kurmak ister misiniz? (manuel kurulum) [e/h]: ")
    if choice.lower() == 'e':
        print("\nTarayıcıda ngrok download sayfası açılıyor...")
        import webbrowser
        webbrowser.open('https://ngrok.com/download')
    sys.exit(1)


def start_ngrok_tunnel(port=8888):
    """ngrok tunnel başlat"""
    print(f"\n🔧 ngrok tunnel başlatılıyor (port {port})...")

    # ngrok'u arka planda başlat
    proc = subprocess.Popen(
        ['ngrok', 'http', str(port), '--log=stdout'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Tunnel URL'yi bul
    time.sleep(3)  # ngrok'un başlaması için bekle

    # API'den tunnel URL'yi al
    try:
        import requests
        response = requests.get('http://localhost:4040/api/tunnels')
        tunnels = response.json()['tunnels']
        for tunnel in tunnels:
            if tunnel['proto'] == 'https':
                return proc, tunnel['public_url']
    except:
        pass

    print("❌ ngrok tunnel URL'si alınamadı!")
    print("Manuel olarak kontrol edin: http://localhost:4040")
    proc.kill()
    return None, None


def ngrok_auth():
    """ngrok ile OAuth"""
    Config.validate()

    # ngrok kontrolü
    if not check_ngrok():
        install_ngrok()

    print("\n" + "=" * 70)
    print("SPOTIFY OAUTH - NGROK HTTPS TUNNEL")
    print("=" * 70)

    # ngrok tunnel başlat
    ngrok_proc, public_url = start_ngrok_tunnel(8888)

    if not public_url:
        print("❌ ngrok başlatılamadı!")
        sys.exit(1)

    redirect_uri = f"{public_url}/callback"

    print(f"\n✅ ngrok tunnel aktif!")
    print(f"   Public URL: {public_url}")
    print(f"   Redirect URI: {redirect_uri}")

    print("\n" + "=" * 70)
    print("ÖNEMLİ: SPOTIFY DASHBOARD AYARLARI")
    print("=" * 70)
    print(f"""
1. https://developer.spotify.com/dashboard adresine gidin
2. Uygulamanızı açın
3. Settings > Redirect URIs
4. Şu URI'yi ekleyin:

   {redirect_uri}

5. SAVE butonuna tıklayın
6. Geri dönün ve ENTER'a basın
""")

    input("Dashboard'da Redirect URI'yi ekledikten sonra ENTER'a basın...")

    try:
        # OAuth flow
        auth_manager = SpotifyOAuth(
            client_id=Config.SPOTIFY_CLIENT_ID,
            client_secret=Config.SPOTIFY_CLIENT_SECRET,
            redirect_uri=redirect_uri,
            scope=Config.SPOTIFY_SCOPE,
            cache_path='.cache',
            open_browser=True
        )

        # Token al
        token_info = auth_manager.get_access_token(as_dict=False)

        print("\n" + "=" * 70)
        print("✅ BAŞARILI!")
        print("=" * 70)
        print(f"\nToken kaydedildi: .cache")
        print("\nngrok tunnel'ı kapatabilirsiniz (Ctrl+C)")
        print("\nArtık uygulamayı normal şekilde kullanabilirsiniz:")
        print("  ./start.sh")

    except Exception as e:
        print(f"\n❌ OAuth hatası: {e}")

    finally:
        # ngrok'u kapat
        print("\nngrok kapatılıyor...")
        ngrok_proc.terminate()
        try:
            ngrok_proc.wait(timeout=5)
        except:
            ngrok_proc.kill()


if __name__ == "__main__":
    try:
        ngrok_auth()
    except KeyboardInterrupt:
        print("\n\nİptal edildi.")
        sys.exit(0)
