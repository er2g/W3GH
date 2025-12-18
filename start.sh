#!/bin/bash
# Hızlı başlatma scripti

echo "🎵 Spotify Autoplay başlatılıyor..."

# Credentials kontrolü
if [ ! -f ".spotify_credentials.json" ]; then
    echo "❌ Credentials bulunamadı!"
    echo ""
    echo "Önce Spotify API kurulumu yapın:"
    echo "  python3 auth_manual.py"
    exit 1
fi

# Python scriptini çalıştır
python3 spotify_autoplay.py
