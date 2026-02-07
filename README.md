# SilentDJ Spotify

Linux-based Spotify autoplay controller with a Flask web panel for authentication, playback control, and device management.

## Features

- Web-based Spotify OAuth setup
- Dashboard for playback/device status
- Idle-time autoplay trigger
- Playlist/artist-based loop workflows
- Service scripts for install/start/stop flows

## Requirements

- Ubuntu/Debian environment
- Python 3.8+
- Spotify Premium account

## Install

```bash
pip3 install --user -r requirements.txt
```

## Start Web Panel

```bash
./start_web.sh
```

## Optional Service Setup

- `install.sh`: install and configure helpers
- `spotify-autoplay.service`: systemd unit template
- `uninstall.sh`: cleanup

## Project Layout

- `app.py`: Flask web app
- `spotify_service.py`: Spotify integration logic
- `templates/`: web templates
