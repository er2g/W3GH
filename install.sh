#!/bin/bash
# Spotify Autoplay Kurulum Scripti

set -e

echo "================================================"
echo "Spotify Autoplay - Death Albums Loop"
echo "Kurulum Scripti"
echo "================================================"
echo ""

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Hata fonksiyonu
error() {
    echo -e "${RED}[HATA]${NC} $1"
    exit 1
}

success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

info() {
    echo -e "[i] $1"
}

# Python3 kontrolü
info "Python3 kontrolü yapılıyor..."
if ! command -v python3 &> /dev/null; then
    error "Python3 bulunamadı. Lütfen Python3'ü kurun: sudo apt-get install python3"
fi
success "Python3 bulundu: $(python3 --version)"

# Pip kontrolü
info "pip kontrolü yapılıyor..."
if ! command -v pip3 &> /dev/null; then
    warning "pip3 bulunamadı, kuruluyor..."
    sudo apt-get update
    sudo apt-get install -y python3-pip
fi
success "pip3 bulundu"

# Virtual environment kurulumu
info "Python virtual environment oluşturuluyor..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    success "Virtual environment oluşturuldu"
else
    success "Virtual environment zaten mevcut"
fi

# Activate ve dependencies kurulumu
info "Python bağımlılıkları yükleniyor..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
success "Bağımlılıklar yüklendi"

# .env dosyası kontrolü
if [ ! -f ".env" ]; then
    warning ".env dosyası bulunamadı"
    echo ""
    echo "Spotify API ayarları için .env dosyası oluşturuluyor..."
    cp .env.example .env
    echo ""
    echo "================================================"
    echo "ÖNEMLİ: Spotify API Ayarları"
    echo "================================================"
    echo ""
    echo "Spotify API kullanabilmek için Developer Dashboard'da"
    echo "uygulama oluşturmanız gerekiyor."
    echo ""
    echo "İki seçeneğiniz var:"
    echo ""
    echo "1) Otomatik kurulum yardımcısı (ÖNERİLEN)"
    echo "   - Adım adım rehberlik"
    echo "   - Tarayıcıda sayfaları otomatik açar"
    echo ""
    echo "2) Manuel kurulum"
    echo "   - .env dosyasını elle düzenlersiniz"
    echo "   - README.md'deki talimatları takip edersiniz"
    echo ""
    read -p "Otomatik kurulum yardımcısını kullanmak ister misiniz? [e/h]: " use_helper

    if [[ $use_helper =~ ^[Ee]$ ]]; then
        echo ""
        info "Kurulum yardımcısı başlatılıyor..."
        python setup_spotify_auth.py
    else
        echo ""
        warning "Manuel kurulum seçildi"
        echo ""
        echo "Yapmanız gerekenler:"
        echo ""
        echo "1. https://developer.spotify.com/dashboard adresine gidin"
        echo "2. 'Create app' ile yeni bir uygulama oluşturun"
        echo "3. Uygulama ayarlarından:"
        echo "   - Client ID"
        echo "   - Client Secret"
        echo "   bilgilerini alın"
        echo ""
        echo "4. ÇOK ÖNEMLİ: Redirect URI olarak ekleyin:"
        echo "   http://localhost:8888/callback"
        echo ""
        echo "   DİKKAT:"
        echo "   - https DEĞIL http olmalı"
        echo "   - Tam olarak bu şekilde yazın"
        echo "   - Dashboard'da 'Save' butonuna tıklayın!"
        echo ""
        echo "5. .env dosyasını düzenleyin:"
        echo "   nano .env"
        echo ""
        read -p "Devam etmek için ENTER'a basın..."

        # Nano ile dosyayı aç
        nano .env
    fi
else
    success ".env dosyası mevcut"
fi

# Executable yapma
info "Script dosyaları executable yapılıyor..."
chmod +x spotify_autoplay.py
chmod +x setup_virtual_audio.sh
success "Script dosyaları hazır"

# Sanal ses kartı kurulumu
echo ""
echo "================================================"
echo "Sanal Ses Kartı Kurulumu"
echo "================================================"
echo ""
read -p "Sanal ses kartı kurmak istiyor musunuz? (Sunucu için gerekli) [e/h]: " install_audio

if [[ $install_audio =~ ^[Ee]$ ]]; then
    sudo ./setup_virtual_audio.sh
    success "Sanal ses kartı kuruldu"
else
    warning "Sanal ses kartı kurulumu atlandı"
fi

# Systemd service kurulumu
echo ""
echo "================================================"
echo "Systemd Service Kurulumu"
echo "================================================"
echo ""
read -p "Otomatik başlatma servisi kurmak istiyor musunuz? [e/h]: " install_service

if [[ $install_service =~ ^[Ee]$ ]]; then
    info "Systemd servisi kuruluyor..."

    # Service dosyasını kopyala
    sudo cp spotify-autoplay.service /etc/systemd/system/spotify-autoplay@.service

    # Systemd'yi yenile
    sudo systemctl daemon-reload

    # Servisi aktifleştir
    sudo systemctl enable spotify-autoplay@$USER.service

    success "Systemd servisi kuruldu"
    echo ""
    echo "Servisi başlatmak için:"
    echo "  sudo systemctl start spotify-autoplay@$USER.service"
    echo ""
    echo "Servis durumunu kontrol etmek için:"
    echo "  sudo systemctl status spotify-autoplay@$USER.service"
    echo ""
    echo "Log'ları görüntülemek için:"
    echo "  tail -f spotify_autoplay.log"
    echo "  sudo journalctl -u spotify-autoplay@$USER.service -f"
else
    warning "Systemd servisi kurulumu atlandı"
fi

echo ""
echo "================================================"
echo "✓ Kurulum Tamamlandı!"
echo "================================================"
echo ""
echo "Manuel olarak başlatmak için:"
echo "  source venv/bin/activate"
echo "  python spotify_autoplay.py"
echo ""
echo "İlk çalıştırmada:"
echo "1. Tarayıcıda Spotify oturum açma sayfası açılacak"
echo "2. Giriş yapın ve uygulamayı yetkilendirin"
echo "3. Yönlendirilen URL'i kopyalayın ve terminale yapıştırın"
echo ""
echo "Özellikler:"
echo "- ${Config.IDLE_TIME_MINUTES} dakika boşta kalınca Death albümleri çalar"
echo "- Loop modunda sürekli çalar"
echo "- Kullanıcı müdahale edince (durdur/başlat/atla) otomatik mod kapanır"
echo "- 30 dakika sonra tekrar otomatik başlar"
echo ""
