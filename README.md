# 🎵 Spotify Otomatik Çalma Sistemi - Death Loop

Ubuntu/Linux için Spotify otomatik çalma uygulaması. Belirli bir süre (varsayılan 30 dakika) Spotify'da herhangi bir kullanıcı aktivitesi olmadığında, otomatik olarak **Death** grubunun albümlerini loop modunda çalar.

## 🎯 Özellikler

- ✅ **Otomatik Başlatma**: 30 dakika boşta kalınca Death albümleri otomatik çalar
- ✅ **Kullanıcı Kontrolü**: Şarkı durdurma/başlatma/atlama ile otomatik mod kapanır
- ✅ **Loop Modu**: Tüm Death albümleri sürekli döngüde çalar
- ✅ **Sanal Sunucu Desteği**: Sanal ses kartı ile headless sunucularda çalışır
- ✅ **Systemd Servisi**: Sistem başlangıcında otomatik başlar
- ✅ **Detaylı Logging**: Tüm aktiviteler loglanır

## 🎸 Death Grubu Hakkında

[Death](https://open.spotify.com/artist/1Dvfqq39HxvCJ3GvfeIFuT), Chuck Schuldiner tarafından 1983'te kurulan ve death metal türünün öncülerinden olan efsanevi bir gruptur.

**Ünlü Albümleri:**
- Scream Bloody Gore (1987)
- Leprosy (1988)
- Spiritual Healing (1990)
- Human (1991)
- Individual Thought Patterns (1993)
- Symbolic (1995)
- The Sound of Perseverance (1998)

## 📋 Gereksinimler

- **İşletim Sistemi**: Ubuntu 20.04+ (Debian tabanlı dağıtımlar)
- **Python**: 3.8+
- **Spotify**: Premium hesap (API kontrolü için gerekli)
- **Ses**: PulseAudio (sanal sunucu için sanal ses kartı)

## 🚀 Kurulum

### 1. Repoyu Klonlayın

```bash
git clone https://github.com/YOUR_USERNAME/W3GH.git
cd W3GH
```

### 2. Kurulum Scriptini Çalıştırın

```bash
chmod +x install.sh
./install.sh
```

Kurulum scripti şunları yapacak:
1. Python bağımlılıklarını kurar
2. `.env` dosyasını oluşturur
3. Sanal ses kartı kurulumu (opsiyonel)
4. Systemd servisi kurulumu (opsiyonel)

### 3. Spotify API Ayarları

#### Otomatik Kurulum Yardımcısı (Önerilen)

En kolay yol, interaktif kurulum yardımcısını kullanmak:

```bash
source venv/bin/activate
python setup_spotify_auth.py
```

Bu script size adım adım rehberlik edecek ve tarayıcıda gerekli sayfaları açacaktır.

#### Manuel Kurulum

**Adım 1: Developer Dashboard'a Giriş**

1. [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)'a gidin
2. Spotify hesabınızla giriş yapın
3. İlk kez kullanıyorsanız, kullanım şartlarını kabul edin

**Adım 2: Uygulama Oluşturun**

1. "Create app" butonuna tıklayın
2. Formu doldurun:
   ```
   App name:         Spotify Autoplay
   App description:  Death albums autoplay system
   Website:          http://localhost
   Redirect URI:     http://localhost:8888/callback
   ```
3. "Web API" seçeneğini işaretleyin
4. Kullanım şartlarını kabul edin
5. "Save" butonuna tıklayın

**Adım 3: Redirect URI Ayarları (ÇOK ÖNEMLİ!)**

⚠️ **Bu adım kritik! Redirect URI yanlışsa uygulama çalışmaz.**

1. Oluşturduğunuz uygulamaya tıklayın
2. "Settings" butonuna tıklayın
3. "Redirect URIs" bölümünü bulun
4. Şu URI'yi ekleyin (TAMAMEN aynı şekilde):
   ```
   http://localhost:8888/callback
   ```

   **Dikkat edilecekler:**
   - `https` DEĞIL, `http` olmalı (localhost için HTTP kabul edilir)
   - Sonda `/` olmamalı
   - Büyük/küçük harf önemli
   - Port numarası `:8888` olmalı

5. "Add" butonuna tıklayın
6. **"Save" butonuna tıklamayı unutmayın!**

**Alternatif Redirect URI:**

Bazı sistemlerde `localhost` yerine `127.0.0.1` kullanmak daha iyi çalışır:
```
http://127.0.0.1:8888/callback
```

İsterseniz her iki URI'yi de ekleyebilirsiniz. Hangisini kullanırsanız, `.env` dosyasında aynısını belirtmelisiniz.

**Adım 4: Client ID ve Secret**

1. "Settings" sayfasında "Basic Information" bölümünü bulun
2. **Client ID**'yi kopyalayın (görünür durumda)
3. **Client Secret**'i almak için:
   - "View client secret" linkine tıklayın
   - Görünen Secret'i kopyalayın
   - ⚠️ **Secret'i kimseyle paylaşmayın!**

**Adım 5: .env Dosyasını Düzenleyin**

```bash
nano .env
```

Şu bilgileri girin:

```env
# Spotify API bilgileri (ZORUNLU)
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here

# Redirect URI - Dashboard'da eklediğiniz ile AYNI olmalı!
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback

# Veya 127.0.0.1 kullanıyorsanız:
# SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback

# Zamanlama ayarları
IDLE_TIME_MINUTES=30
CHECK_INTERVAL_SECONDS=60
```

**Kaydet ve çık** (nano'da: `Ctrl+X`, `Y`, `Enter`)

### 4. İlk Çalıştırma

```bash
source venv/bin/activate
python spotify_autoplay.py
```

İlk çalıştırmada:
1. Tarayıcıda Spotify oturum açma sayfası açılır
2. Giriş yapın ve uygulamayı yetkilendirin
3. Yönlendirilen URL'i kopyalayın (http://localhost:8888/callback?code=...)
4. Terminale yapıştırın

Artık uygulama çalışıyor! `.cache` dosyası oluşturuldu, bir daha giriş yapmanıza gerek yok.

## 🖥️ Sanal Sunucu Kurulumu

Sanal sunucuda (VPS) çalıştırmak için sanal ses kartı gereklidir:

### Otomatik Kurulum

```bash
sudo ./setup_virtual_audio.sh
```

### Manuel Kurulum

```bash
# PulseAudio kurulumu
sudo apt-get update
sudo apt-get install -y pulseaudio pulseaudio-utils

# PulseAudio'yu başlat
pulseaudio --start

# Sanal ses cihazı oluştur
pactl load-module module-null-sink sink_name=spotify_sink sink_properties=device.description="Spotify_Virtual_Output"

# Kalıcı yapmak için /etc/pulse/default.pa dosyasına ekleyin:
echo 'load-module module-null-sink sink_name=spotify_sink sink_properties=device.description="Spotify_Virtual_Output"' | sudo tee -a /etc/pulse/default.pa
```

### Spotify'ı Sanal Cihaza Yönlendirme

Spotify web player veya desktop uygulaması kullanıyorsanız:

1. Spotify ayarlarından ses çıkışını değiştirin
2. Veya `pavucontrol` kullanın:

```bash
sudo apt-get install pavucontrol
pavucontrol
```

## 🔧 Systemd Servisi (Otomatik Başlatma)

### Servisi Başlatma

```bash
sudo systemctl start spotify-autoplay@$USER.service
```

### Servisi Durdurma

```bash
sudo systemctl stop spotify-autoplay@$USER.service
```

### Servis Durumu

```bash
sudo systemctl status spotify-autoplay@$USER.service
```

### Log Görüntüleme

```bash
# Uygulama log'u
tail -f spotify_autoplay.log

# Systemd log'u
sudo journalctl -u spotify-autoplay@$USER.service -f
```

### Otomatik Başlatmayı Devre Dışı Bırakma

```bash
sudo systemctl disable spotify-autoplay@$USER.service
```

## 📖 Kullanım

### Nasıl Çalışır?

1. **Normal Kullanım**: Spotify'ı normal şekilde kullanın
2. **Boşta Kalma**: 30 dakika boyunca hiçbir aktivite olmazsa (şarkı değiştirme, durdurma, başlatma)
3. **Otomatik Başlatma**: Death albümleri otomatik çalmaya başlar (loop modunda)
4. **Kullanıcı Müdahalesi**: Herhangi bir müdahale (durdur/başlat/atla) otomatik modu kapatır
5. **Tekrar Bekleme**: Sistem tekrar 30 dakika bekler

### Örnek Senaryolar

#### Senaryo 1: Normal Kullanım
```
09:00 - Spotify'da kendi müziğinizi dinliyorsunuz
09:30 - Şarkıyı durdurdunuz
10:00 - 30 dakika geçti, Death otomatik başladı
10:15 - Başka bir şarkı açtınız → Otomatik mod kapandı
```

#### Senaryo 2: Uzun Süre Boşta
```
14:00 - Son şarkınızı durdurdunuz
14:30 - Death otomatik başladı
     - Tüm gün Death çalmaya devam eder (loop)
```

### Ayarlar

`.env` dosyasından ayarları değiştirebilirsiniz:

```env
# Boşta kalma süresi (dakika)
IDLE_TIME_MINUTES=30

# Kontrol aralığı (saniye)
CHECK_INTERVAL_SECONDS=60
```

Değişikliklerden sonra servisi yeniden başlatın:

```bash
sudo systemctl restart spotify-autoplay@$USER.service
```

## 🐛 Sorun Giderme

### "No active device found" Hatası

**Sorun**: Aktif Spotify cihazı bulunamıyor.

**Çözüm**:
1. Spotify uygulamasını açın (web veya desktop)
2. Bir şarkı çalmaya başlayın
3. Scripti tekrar çalıştırın

### "Could not authenticate" / "Invalid redirect URI" Hatası

**Sorun**: Spotify API kimlik doğrulama hatası veya redirect URI uyuşmazlığı.

Bu en sık karşılaşılan hatadır! Redirect URI'nin tam olarak eşleşmesi gerekir.

**Çözüm 1: Redirect URI Kontrolü (En Sık Çözüm)**

1. `.env` dosyanızdaki URI'yi kontrol edin:
   ```bash
   cat .env | grep REDIRECT
   ```

2. Spotify Dashboard'da kontrol edin:
   - https://developer.spotify.com/dashboard
   - Uygulamanızı açın
   - Settings > Redirect URIs
   - `.env` dosyasındaki ile TAM OLARAK aynı olmalı!

3. Sık yapılan hatalar:
   - ❌ `http://localhost:8888/callback/` (sonda `/` var)
   - ❌ `https://localhost:8888/callback` (`https` kullanılmış)
   - ❌ `http://localhost/callback` (port eksik)
   - ✅ `http://localhost:8888/callback` (DOĞRU)

4. Dashboard'da değişiklik yaptıysanız **"Save" butonuna tıklamayı unutmayın!**

**Çözüm 2: Alternatif URI Deneyin**

Bazı sistemlerde `localhost` yerine `127.0.0.1` daha iyi çalışır:

1. Spotify Dashboard'a ekleyin:
   ```
   http://127.0.0.1:8888/callback
   ```

2. `.env` dosyasını güncelleyin:
   ```env
   SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
   ```

3. `.cache` dosyasını silin ve tekrar deneyin:
   ```bash
   rm .cache*
   source venv/bin/activate
   python spotify_autoplay.py
   ```

**Çözüm 3: Client ID/Secret Kontrolü**

1. `.env` dosyasındaki Client ID ve Secret'i kontrol edin:
   ```bash
   cat .env
   ```

2. Boşluk, satır sonu, veya fazladan karakter olmamalı

3. Dashboard'dan tekrar kopyalayın

**Çözüm 4: Tamamen Yeni Başlangıç**

```bash
# Cache'i temizle
rm -f .cache*

# Kurulum yardımcısını çalıştır
source venv/bin/activate
python setup_spotify_auth.py

# Test et
python test_spotify.py
```

### Sanal Ses Kartı Çalışmıyor

**Sorun**: PulseAudio sanal cihazı bulunamıyor.

**Çözüm**:
```bash
# PulseAudio'yu yeniden başlat
pulseaudio -k
pulseaudio --start

# Sanal cihazı tekrar oluştur
pactl load-module module-null-sink sink_name=spotify_sink

# Cihazları listele
pactl list sinks short
```

### Servis Başlamıyor

**Sorun**: Systemd servisi başlatılamıyor.

**Çözüm**:
```bash
# Log'ları kontrol et
sudo journalctl -u spotify-autoplay@$USER.service -n 50

# Manuel çalıştırıp test et
source venv/bin/activate
python spotify_autoplay.py

# Servis dosyasını kontrol et
sudo systemctl status spotify-autoplay@$USER.service
```

## 📊 Log Dosyaları

- `spotify_autoplay.log` - Uygulama log'ları
- `service.log` - Systemd service stdout
- `service_error.log` - Systemd service stderr

## 🔒 Güvenlik

- `.env` dosyası `.gitignore`'da (API anahtarları paylaşılmaz)
- `.cache` dosyası yerel (Spotify token'ları)
- Systemd servisi kullanıcı yetkileriyle çalışır (root değil)

## 🛠️ Geliştirme

### Farklı Sanatçı Kullanma

`spotify_autoplay.py` dosyasında `_find_death_albums()` fonksiyonunu değiştirin:

```python
def _find_death_albums(self):
    # "Death" yerine istediğiniz sanatçıyı yazın
    results = self.sp.search(q='artist:YourArtistName', type='artist', limit=10)
    # ...
```

### Boşta Kalma Süresini Değiştirme

`.env` dosyasında:

```env
# 15 dakika için
IDLE_TIME_MINUTES=15

# 1 saat için
IDLE_TIME_MINUTES=60
```

## 📝 Lisans

Bu proje MIT lisansı altındadır.

## 🤝 Katkıda Bulunma

Pull request'ler memnuniyetle karşılanır!

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📧 İletişim

Sorularınız için issue açabilirsiniz.

## 🎵 Death'e Saygılarımla

> "Life is but a dream for the dead"
> — Chuck Schuldiner, Death

---

**Not**: Bu proje Spotify Premium hesap gerektirir. Spotify API kullanım koşullarına uygun olarak kullanın.
