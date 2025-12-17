#!/bin/bash
# Sanal ses kartı kurulum scripti
# Ubuntu/Debian için PulseAudio dummy sink oluşturur

echo "================================================"
echo "Spotify Sanal Ses Kartı Kurulum Scripti"
echo "================================================"
echo ""

# Root kontrolü
if [ "$EUID" -ne 0 ]; then
    echo "Bu script root yetkisiyle çalıştırılmalı: sudo $0"
    exit 1
fi

echo "[1/4] PulseAudio kurulumu kontrol ediliyor..."
if ! command -v pulseaudio &> /dev/null; then
    echo "PulseAudio bulunamadı, kuruluyor..."
    apt-get update
    apt-get install -y pulseaudio pulseaudio-utils
else
    echo "✓ PulseAudio zaten kurulu"
fi

echo ""
echo "[2/4] Sanal ses cihazı (dummy sink) oluşturuluyor..."

# PulseAudio'nun çalıştığından emin ol
sudo -u $SUDO_USER pulseaudio --check
if [ $? -ne 0 ]; then
    echo "PulseAudio başlatılıyor..."
    sudo -u $SUDO_USER pulseaudio --start
    sleep 2
fi

# Dummy sink oluştur
sudo -u $SUDO_USER pactl load-module module-null-sink sink_name=spotify_sink sink_properties=device.description="Spotify_Virtual_Output"

if [ $? -eq 0 ]; then
    echo "✓ Sanal ses cihazı oluşturuldu: spotify_sink"
else
    echo "⚠ Sanal ses cihazı zaten mevcut veya oluşturulamadı"
fi

echo ""
echo "[3/4] Kalıcı yapılandırma ayarlanıyor..."

# PulseAudio config dosyası
CONFIG_FILE="/etc/pulse/default.pa"
BACKUP_FILE="/etc/pulse/default.pa.backup"

# Backup al
if [ ! -f "$BACKUP_FILE" ]; then
    cp "$CONFIG_FILE" "$BACKUP_FILE"
    echo "✓ Yedek alındı: $BACKUP_FILE"
fi

# Eğer zaten eklenmemişse, dummy sink'i config'e ekle
if ! grep -q "spotify_sink" "$CONFIG_FILE"; then
    echo "" >> "$CONFIG_FILE"
    echo "# Spotify sanal ses cihazı" >> "$CONFIG_FILE"
    echo "load-module module-null-sink sink_name=spotify_sink sink_properties=device.description=\"Spotify_Virtual_Output\"" >> "$CONFIG_FILE"
    echo "✓ Kalıcı konfigürasyon eklendi"
else
    echo "✓ Kalıcı konfigürasyon zaten mevcut"
fi

echo ""
echo "[4/4] Mevcut ses cihazları listeleniyor..."
sudo -u $SUDO_USER pactl list sinks short

echo ""
echo "================================================"
echo "✓ Kurulum tamamlandı!"
echo "================================================"
echo ""
echo "Sanal ses cihazı: spotify_sink"
echo ""
echo "Spotify'ı bu cihaza yönlendirmek için:"
echo "1. Spotify uygulamasını açın"
echo "2. Ayarlar > Ses çıkışı"
echo "3. 'Spotify_Virtual_Output' seçin"
echo ""
echo "Veya pavucontrol kullanın:"
echo "  sudo apt-get install pavucontrol"
echo "  pavucontrol"
echo ""
echo "PulseAudio'yu yeniden başlatmak için:"
echo "  pulseaudio -k && pulseaudio --start"
echo ""
