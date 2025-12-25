#!/bin/bash
# Spotify Web Yönetim Paneli Başlatma

echo "🎵 Spotify Web Yönetim Paneli başlatılıyor..."
echo ""

# Çalışma dizinine git
cd "$(dirname "$0")"

# Python kontrolü
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 bulunamadı!"
    exit 1
fi

# Flask kontrolü
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Flask yükleniyor..."
    pip3 install --user flask
fi

# Spotipy kontrolü
if ! python3 -c "import spotipy" 2>/dev/null; then
    echo "📦 Spotipy yükleniyor..."
    pip3 install --user spotipy requests
fi

echo ""
echo "🌐 Web paneli başlatılıyor..."
echo "   Adres: http://localhost:5000"
echo ""
echo "   Durdurmak için Ctrl+C"
echo ""

# Flask uygulamasını başlat
python3 app.py
