#!/bin/bash
# Hızlı başlatma scripti

echo "🎵 Spotify Autoplay başlatılıyor..."

# Virtual environment'ı aktifleştir
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment bulunamadı!"
    echo "Önce install.sh scriptini çalıştırın."
    exit 1
fi

# .env dosyası kontrolü
if [ ! -f ".env" ]; then
    echo "❌ .env dosyası bulunamadı!"
    echo "Lütfen .env.example dosyasını kopyalayın ve düzenleyin:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

# Python scriptini çalıştır
python spotify_autoplay.py
