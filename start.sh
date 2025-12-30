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

# Web uygulamasını başlat
python3 app.py
