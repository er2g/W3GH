#!/usr/bin/env python3
"""
Spotify API Kurulum Yardımcısı
Adım adım Spotify Developer Dashboard ayarları
"""
import sys
import os
import webbrowser


def print_header(text):
    """Başlık yazdır"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_step(number, text):
    """Adım yazdır"""
    print(f"\n{'─' * 70}")
    print(f"[ADIM {number}] {text}")
    print('─' * 70)


def wait_for_user():
    """Kullanıcının devam etmesini bekle"""
    input("\n✓ Tamamladım, devam et (ENTER tuşuna bas)...")


def main():
    """Ana kurulum yardımcısı"""
    print_header("🎵 Spotify API Kurulum Yardımcısı")

    print("""
Bu yardımcı, Spotify Developer Dashboard'da uygulama oluşturmanız
ve gerekli ayarları yapmanız için size rehberlik edecek.

Spotify API kullanabilmek için:
  ✓ Spotify hesabınız olmalı (Premium olması gerekmez)
  ✓ Spotify Developer Dashboard'da uygulama oluşturmalısınız
  ✓ Client ID ve Client Secret almanız gerekir
""")

    ready = input("Hazır mısınız? [e/h]: ")
    if ready.lower() != 'e':
        print("Kurulum iptal edildi.")
        sys.exit(0)

    # ADIM 1: Developer Dashboard'a git
    print_step(1, "Spotify Developer Dashboard'a Giriş")
    print("""
1. Aşağıdaki URL'yi açın:
   https://developer.spotify.com/dashboard

2. Spotify hesabınızla giriş yapın

3. Eğer ilk kez kullanıyorsanız, kullanım şartlarını kabul edin
""")

    open_browser = input("\nTarayıcıda otomatik açmak ister misiniz? [e/h]: ")
    if open_browser.lower() == 'e':
        webbrowser.open('https://developer.spotify.com/dashboard')
        print("✓ Tarayıcı açıldı")

    wait_for_user()

    # ADIM 2: Uygulama oluştur
    print_step(2, "Yeni Uygulama Oluşturun")
    print("""
1. Dashboard'da "Create app" butonuna tıklayın

2. Uygulama bilgilerini doldurun:
   ┌────────────────────────────────────────────────┐
   │ App name:         Spotify Autoplay             │
   │ App description:  Death albums autoplay system │
   │ Website:          http://localhost             │
   │ Redirect URI:     http://localhost:8888/callback │
   │                   (ÖNEMLİ! Tam olarak yazın)  │
   └────────────────────────────────────────────────┘

3. "Web API" seçeneğini işaretleyin

4. Kullanım şartlarını kabul edin

5. "Save" butonuna tıklayın
""")

    wait_for_user()

    # ADIM 3: Redirect URI ekle/kontrol et
    print_step(3, "Redirect URI Kontrolü (ÇOK ÖNEMLİ!)")
    print("""
Bu adım çok önemli! Redirect URI yanlışsa uygulama çalışmaz.

1. Oluşturduğunuz uygulamayı açın

2. "Settings" butonuna tıklayın

3. "Redirect URIs" bölümünü bulun

4. Şu URI'nin ekli olduğundan emin olun:
   ┌────────────────────────────────────────┐
   │ http://localhost:8888/callback         │
   └────────────────────────────────────────┘

   ⚠️  UYARI:
   - Tam olarak "http://localhost:8888/callback" yazmalı
   - "https" DEĞIL, "http" olmalı (localhost için)
   - Sonda "/" olmamalı
   - Büyük/küçük harf önemli

5. Eğer eklenmemişse:
   - "Add URI" tıklayın
   - http://localhost:8888/callback yazın
   - "Add" tıklayın
   - "Save" tıklayın (ÇOK ÖNEMLİ!)

6. Alternatif: Bazı sistemlerde şu daha iyi çalışabilir:
   - http://127.0.0.1:8888/callback
   (İsterseniz ikisini birden ekleyebilirsiniz)
""")

    wait_for_user()

    # ADIM 4: Client ID ve Secret al
    print_step(4, "Client ID ve Client Secret'i Alın")
    print("""
1. Uygulama ayarları sayfasında "Basic Information" bölümünü bulun

2. Client ID'yi kopyalayın:
   - Görünür durumda olacak
   - Kopyala butonuna tıklayın
   - Bir yere not edin

3. Client Secret'i alın:
   - "View client secret" linkine tıklayın
   - Secret görünür olacak
   - Kopyala butonuna tıklayın
   - Bir yere not edin

   ⚠️  UYARI: Client Secret'i kimseyle paylaşmayın!
""")

    wait_for_user()

    # ADIM 5: .env dosyası oluştur
    print_step(5, ".env Dosyası Oluşturun")

    # .env.example var mı kontrol et
    if not os.path.exists('.env.example'):
        print("❌ .env.example dosyası bulunamadı!")
        print("   Proje dizininde olduğunuzdan emin olun.")
        sys.exit(1)

    # .env var mı kontrol et
    env_exists = os.path.exists('.env')

    if env_exists:
        print("⚠️  .env dosyası zaten mevcut!")
        overwrite = input("Üzerine yazmak ister misiniz? [e/h]: ")
        if overwrite.lower() != 'e':
            print("\nMevcut .env dosyasını elle düzenleyin:")
            print("  nano .env")
            print("\nVeya:")
            print("  code .env")
            wait_for_user()
        else:
            os.system('cp .env.example .env')
            print("✓ .env dosyası oluşturuldu")
    else:
        os.system('cp .env.example .env')
        print("✓ .env dosyası oluşturuldu")

    print("""
Şimdi .env dosyasını düzenleyin ve bilgileri girin:

1. .env dosyasını açın:
   nano .env

   veya favori editörünüzle:
   code .env
   vim .env

2. Şu satırları bulun ve değiştirin:

   SPOTIFY_CLIENT_ID=your_client_id_here
   → SPOTIFY_CLIENT_ID=<kopyaladığınız_client_id>

   SPOTIFY_CLIENT_SECRET=your_client_secret_here
   → SPOTIFY_CLIENT_SECRET=<kopyaladığınız_client_secret>

3. SPOTIFY_REDIRECT_URI'yi kontrol edin:
   SPOTIFY_REDIRECT_URI=http://localhost:8888/callback

   Eğer 127.0.0.1 kullanacaksanız:
   SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback

   ⚠️  Dashboard'da eklediğiniz URI ile AYNI olmalı!

4. Kaydedin ve çıkın
   (nano'da: Ctrl+X, Y, Enter)
""")

    edit_now = input("\nŞimdi düzenlemek ister misiniz? [e/h]: ")
    if edit_now.lower() == 'e':
        os.system('nano .env')

    # ADIM 6: Test et
    print_step(6, "Bağlantıyı Test Edin")
    print("""
Artık Spotify API bağlantısını test edebilirsiniz:

1. Test scriptini çalıştırın:
   source venv/bin/activate
   python test_spotify.py

2. İlk çalıştırmada:
   - Tarayıcıda Spotify login sayfası açılacak
   - Giriş yapın ve "Agree" tıklayın
   - Yönlendirilen URL'i kopyalayın
   - Terminale yapıştırın

3. Başarılı olursa:
   - Kullanıcı bilgileriniz görünecek
   - Aktif cihazlar listelenecek
   - Death grubu bulunacak

4. Sorun olursa:
   - Hata mesajlarını okuyun
   - Redirect URI'yi kontrol edin
   - Client ID/Secret'i kontrol edin
""")

    # Özet
    print_header("✅ Kurulum Tamamlandı!")
    print("""
Tebrikler! Spotify API kurulumunu tamamladınız.

Şimdi yapabilecekleriniz:

1. Bağlantıyı test edin:
   source venv/bin/activate
   python test_spotify.py

2. Uygulamayı başlatın:
   ./start.sh

3. Systemd servisi olarak çalıştırın:
   sudo systemctl start spotify-autoplay@$USER.service

Sorun yaşarsanız README.md dosyasındaki "Sorun Giderme" bölümüne
bakın veya issue açın.

🎵 İyi eğlenceler!
""")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nKurulum iptal edildi.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Hata: {e}")
        sys.exit(1)
