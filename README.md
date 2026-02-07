# 🎵 Spotify Otomatik Çalma Sistemi

Ubuntu/Linux için Spotify otomatik çalma ve web yönetim uygulaması.

## 🎯 Özellikler

### Web Yönetim Paneli
- ✅ **Web Tabanlı Kurulum**: Spotify API'yi tarayıcıdan yapılandırın
- ✅ **OAuth Authentication**: Güvenli web tabanlı Spotify girişi
- ✅ **Dashboard**: Çalma durumu, cihazlar ve kontroller
- ✅ **Cihaz Yönetimi**: Aktif cihazları görün ve yönetin
- ✅ **Cihaz Kilitleme**: Belirli bir cihaza kilitleyin, kaybolursa sistem dursun
- ✅ **Playlist Yönetimi**: Playlistler ve artist albümlerini seçin
- ✅ **Ayarlar**: Tüm yapılandırmayı web'den yönetin
- ✅ **Log İzleme**: Sistem loglarını canlı takip edin

### Otomatik Çalma
- ✅ **Otomatik Başlatma**: Belirlenen süre boşta kalınca otomatik çalma
- ✅ **Kullanıcı Kontrolü**: Şarkı durdurma/başlatma/atlama ile otomatik mod kapanır
- ✅ **Loop Modu**: Seçilen müzik sürekli döngüde çalar
- ✅ **Özelleştirilebilir**: Herhangi bir artist veya playlist seçilebilir

## 📋 Gereksinimler

- **İşletim Sistemi**: Ubuntu 20.04+ (Debian tabanlı)
- **Python**: 3.8+
- **Spotify**: Premium hesap (API kontrolü için gerekli)

## 🚀 Hızlı Kurulum

### 1. Bağımlılıkları Kurun

```bash
pip3 install --user -r requirements.txt
```

### 2. Web Panelini Başlatın

```bash
./start_web.sh
```

veya:

```bash
python3 app.py
```

### 3. Tarayıcıda Açın

```
http://localhost:5000
```

### 4. Kurulum Adımları

1. **API Kurulumu**: Spotify Developer Dashboard'dan Client ID/Secret alın
2. **Spotify Girişi**: Hesabınızla giriş yapın
3. **Cihaz Seçin**: İsterseniz bir cihazı kilitleyin
4. **Ayarları Yapın**: Boşta kalma süresi, playlist, ses seviyesi vb.
5. **Player'ı Başlatın**: Dashboard'dan "Player Başlat" tıklayın

## 🔒 Cihaz Kilitleme

Cihaz kilitleme özelliği ile:
- Müzik sadece seçilen cihazda çalar
- Cihaz çevrimdışı olursa sistem otomatik durur
- Başka cihazlarda istenmeyen çalma önlenir

## 📁 Dosya Yapısı

```
W3GH/
├── app.py                    # Web sunucusu
├── spotify_service.py        # Spotify servis katmanı
├── config.py                 # Konfigürasyon
├── auth_manual.py            # Manuel CLI auth
├── templates/                # HTML şablonları
│   ├── base.html
│   ├── index.html
│   ├── setup.html
│   ├── dashboard.html
│   ├── devices.html
│   ├── playlists.html
│   ├── settings.html
│   └── logs.html
├── start_web.sh              # Web panel başlatma
├── requirements.txt          # Python bağımlılıkları
└── README.md
```

## ⚙️ Ayarlar

Web panelinden ayarlanabilir:

| Ayar | Açıklama | Varsayılan |
|------|----------|------------|
| Boşta Kalma Süresi | Otomatik çalma başlama süresi | 30 dakika |
| Kontrol Aralığı | Durum kontrol periyodu | 60 saniye |
| Artist | Varsayılan artist | Death |
| Ses Seviyesi | Otomatik çalmada ses | 50% |
| Repeat Modu | Tekrar türü | context |
| Shuffle | Karışık çalma | Kapalı |

## 🐛 Sorun Giderme

### "No active device"
Spotify uygulamasını açın ve bir şarkı çalın.

### "Could not authenticate"
```bash
rm -f .cache*
# Web panelden tekrar giriş yapın
```

### Port kullanımda
```bash
# Farklı port ile başlat
python3 -c "from app import app; app.run(port=5001)"
```

## 🔧 Systemd Servisi (Opsiyonel)

CLI modunda systemd servisi için:

```bash
# Servis dosyasını kopyala
sudo cp spotify-autoplay.service /etc/systemd/system/spotify-autoplay@.service

# Servisi başlat
sudo systemctl start spotify-autoplay@$USER.service

# Otomatik başlatma
sudo systemctl enable spotify-autoplay@$USER.service
```

## 📊 Test

```bash
python3 test_spotify.py
```

---

MIT License | Spotify Premium gereklidir
