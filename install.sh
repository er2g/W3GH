#!/bin/bash
# Spotify Autoplay Kurulum Scripti - Basitleştirilmiş

set -e

echo "================================================"
echo "Spotify Autoplay - Death Albums Loop"
echo "Basit Kurulum"
echo "================================================"
echo ""

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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
    error "Python3 bulunamadı. Kurun: sudo apt-get install python3"
fi
success "Python3 bulundu: $(python3 --version)"

# Pip kontrolü
info "pip3 kontrolü yapılıyor..."
if ! command -v pip3 &> /dev/null; then
    warning "pip3 bulunamadı, kuruluyor..."
    sudo apt-get update
    sudo apt-get install -y python3-pip
fi
success "pip3 bulundu"

# Global bağımlılıkları kur
info "Python bağımlılıkları yükleniyor (global)..."
pip3 install --user -r requirements.txt
success "Bağımlılıklar yüklendi"

# Script dosyalarını executable yap
info "Script dosyaları executable yapılıyor..."
chmod +x auth_manual.py
chmod +x app.py
chmod +x setup_virtual_audio.sh
chmod +x start.sh
chmod +x stop.sh
success "Script dosyaları hazır"

# Sanal ses kartı kurulumu
echo ""
echo "================================================"
echo "Sanal Ses Kartı Kurulumu (Opsiyonel)"
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
echo "Systemd Service Kurulumu (Opsiyonel)"
echo "================================================"
echo ""
read -p "Otomatik başlatma servisi kurmak istiyor musunuz? [e/h]: " install_service

if [[ $install_service =~ ^[Ee]$ ]]; then
    info "Systemd servisi kuruluyor..."

    sudo cp spotify-autoplay.service /etc/systemd/system/spotify-autoplay@.service
    sudo systemctl daemon-reload
    sudo systemctl enable spotify-autoplay@$USER.service

    success "Systemd servisi kuruldu"
    echo ""
    echo "Servisi başlatmak için:"
    echo "  sudo systemctl start spotify-autoplay@$USER.service"
else
    warning "Systemd servisi kurulumu atlandı"
fi

echo ""
echo "================================================"
echo "✓ Kurulum Tamamlandı!"
echo "================================================"
echo ""
echo "Şimdi Spotify API kurulumu yapın:"
echo ""
echo "  python3 auth_manual.py"
echo ""
echo "Script size şunları soracak:"
echo "  1. Spotify Client ID"
echo "  2. Spotify Client Secret"
echo "  3. URL kopyala-yapıştır"
echo ""
echo "Sonra uygulamayı başlatın:"
echo "  python3 app.py"
echo ""
echo "veya:"
echo "  ./start.sh"
echo ""
