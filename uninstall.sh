#!/bin/bash
# Kaldırma scripti

echo "================================================"
echo "Spotify Autoplay - Kaldırma"
echo "================================================"
echo ""

# Renk kodları
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

error() {
    echo -e "${RED}[✗]${NC} $1"
}

read -p "Spotify Autoplay sistemini kaldırmak istediğinizden emin misiniz? [e/h]: " confirm

if [[ ! $confirm =~ ^[Ee]$ ]]; then
    echo "Kaldırma iptal edildi."
    exit 0
fi

echo ""
echo "[1/5] Systemd servisi durduruluyor..."
if systemctl is-active --quiet spotify-autoplay@$USER.service; then
    sudo systemctl stop spotify-autoplay@$USER.service
    echo "✓ Servis durduruldu"
fi

echo ""
echo "[2/5] Systemd servisi devre dışı bırakılıyor..."
if systemctl is-enabled --quiet spotify-autoplay@$USER.service 2>/dev/null; then
    sudo systemctl disable spotify-autoplay@$USER.service
    echo "✓ Servis devre dışı bırakıldı"
fi

echo ""
echo "[3/5] Systemd servis dosyası siliniyor..."
if [ -f "/etc/systemd/system/spotify-autoplay@.service" ]; then
    sudo rm /etc/systemd/system/spotify-autoplay@.service
    sudo systemctl daemon-reload
    echo "✓ Servis dosyası silindi"
fi

echo ""
echo "[4/5] Sanal ses kartı kaldırılıyor..."
# PulseAudio config'den kaldır
if [ -f "/etc/pulse/default.pa" ]; then
    if grep -q "spotify_sink" /etc/pulse/default.pa; then
        sudo sed -i '/spotify_sink/d' /etc/pulse/default.pa
        echo "✓ Sanal ses kartı config'den kaldırıldı"
    fi
fi

# Çalışan module'ü kaldır
if pactl list sinks short | grep -q "spotify_sink"; then
    pactl unload-module module-null-sink
    echo "✓ Sanal ses kartı kaldırıldı"
fi

echo ""
echo "[5/5] Dosyalar korunuyor..."
warning "Not: Proje dosyaları (kodlar, .env, log'lar) korunuyor."
warning "Tüm dosyaları silmek için:"
echo "  cd .."
echo "  rm -rf W3GH/"

echo ""
echo "================================================"
echo "✓ Kaldırma tamamlandı"
echo "================================================"
echo ""
echo "Sanal ses kartını tamamen kaldırmak için PulseAudio'yu yeniden başlatın:"
echo "  pulseaudio -k && pulseaudio --start"
echo ""
