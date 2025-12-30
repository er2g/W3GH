#!/bin/bash
# Servisi durdurma scripti

echo "🛑 Spotify Autoplay durduruluyor..."

# Systemd servisini durdur
if systemctl is-active --quiet spotify-autoplay@$USER.service; then
    sudo systemctl stop spotify-autoplay@$USER.service
    echo "✅ Systemd servisi durduruldu"
else
    echo "ℹ️ Systemd servisi zaten durmuş"
fi

# Python process'i varsa durdur
if pgrep -f "app.py" > /dev/null; then
    echo "🔍 Çalışan Python process bulundu, durduruluyor..."
    pkill -f "app.py"
    echo "✅ Python process durduruldu"
else
    echo "ℹ️ Çalışan Python process bulunamadı"
fi

echo "✅ Tamamlandı"
