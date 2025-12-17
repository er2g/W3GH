# 🎵 Spotify Otomatik Çalma Sistemi - Death Loop

Ubuntu/Linux için basit Spotify otomatik çalma uygulaması. 30 dakika Spotify'da aktivite yoksa otomatik olarak **Death** grubunun albümlerini loop modunda çalar.

## 🎯 Özellikler

- ✅ **Otomatik Başlatma**: 30 dakika boşta kalınca Death albümleri çalar
- ✅ **Kullanıcı Kontrolü**: Şarkı durdurma/başlatma/atlama ile otomatik mod kapanır
- ✅ **Loop Modu**: Tüm Death albümleri sürekli döngüde çalar
- ✅ **Sanal Sunucu Desteği**: Sanal ses kartı ile headless sunucularda çalışır
- ✅ **Systemd Servisi**: Sistem başlangıcında otomatik başlar
- ✅ **Basit Kurulum**: Tek komutla hazır!

## 🎸 Death Grubu

[Death](https://open.spotify.com/artist/1Dvfqq39HxvCJ3GvfeIFuT) - Chuck Schuldiner tarafından 1983'te kurulan death metal türünün öncülerinden efsanevi grup.

## 📋 Gereksinimler

- **İşletim Sistemi**: Ubuntu 20.04+ (Debian tabanlı)
- **Python**: 3.8+
- **Spotify**: Premium hesap (API kontrolü için gerekli)

## 🚀 Hızlı Kurulum

### 1. Repository'yi Klonlayın

```bash
git clone <repo_url>
cd W3GH
```

### 2. Kurulum

```bash
./install.sh
```

Kurulum:
- Python bağımlılıklarını kurar (global)
- Sanal ses kartı sorar (opsiyonel)
- Systemd servisi sorar (opsiyonel)

### 3. Spotify API Kurulumu

```bash
python3 auth_manual.py
```

Script şunları soracak:

1. **Spotify Developer Dashboard:**
   - https://developer.spotify.com/dashboard
   - "Create app" oluşturun
   - Client ID ve Secret kopyalayın
   - NOT: Redirect URI GEREKLİ DEĞİL!

2. **Credentials girin:**
   - Client ID
   - Client Secret

3. **OAuth:**
   - Tarayıcıda login
   - "Agree" tıkla
   - Hata sayfası (NORMAL!)
   - URL'i kopyala: `http://example.com/callback?code=...`
   - Terminale yapıştır

✅ Bitti!

### 4. Başlatın

```bash
python3 spotify_autoplay.py
```

## 🐛 Sorun Giderme

### "No active device"
```bash
# Spotify açın, bir şarkı çalın
```

### "Could not authenticate"
```bash
rm -f .cache*
python3 auth_manual.py
```

### "This redirect URI is not secure"
**Normal!** Dummy URL, Dashboard'a eklemeyin. Script URL'deki code'u parse ediyor.

## 📖 Nasıl Çalışır?

```
Normal kullanım → 30 dk boşta → Death çalar → Müdahale → Kapanır → Tekrar bekler
```

## ⚙️ Ayarlar

`.env` dosyası:
```env
IDLE_TIME_MINUTES=30
CHECK_INTERVAL_SECONDS=60
```

## 🔧 Systemd

```bash
# Başlat
sudo systemctl start spotify-autoplay@$USER.service

# Durdur
./stop.sh

# Log
tail -f spotify_autoplay.log
```

## 📊 Test

```bash
python3 test_spotify.py
```

## 🎵 Death'e Saygılarımla

> "Life is but a dream for the dead" — Chuck Schuldiner

---

MIT License | Spotify Premium gereklidir
