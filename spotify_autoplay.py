#!/usr/bin/env python3
"""
W3GH - Spotify AutoPlayer Background Service

This runs continuously and monitors Spotify playback.
When playback stops for X minutes, it starts playing the target artist
on the locked device.
"""
import time
import logging
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from spotify_service import spotify_service
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'autoplay.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Main loop"""
    logger.info("=" * 50)
    logger.info("W3GH Spotify AutoPlayer starting...")
    logger.info("=" * 50)

    # Connect to Spotify
    if not spotify_service.connect():
        logger.error("Failed to connect to Spotify!")
        logger.error("Run the web interface first to authenticate: https://rammfire.com/spo/")
        return

    settings = Config.load_settings()
    logger.info(f"Target artist: {settings.get('target_artist', 'Death')}")
    logger.info(f"Wait time after stop: {settings.get('idle_time_minutes', 5)} minutes")
    logger.info(f"Autoplay enabled: {settings.get('autoplay_enabled', True)}")
    logger.info(f"Locked device: {settings.get('locked_device_id', 'Not set')}")

    if not settings.get('locked_device_id'):
        logger.warning("WARNING: No device locked! Go to web interface to lock a device.")

    check_interval = settings.get('check_interval_seconds', 30)
    logger.info(f"Check interval: {check_interval} seconds")
    logger.info("=" * 50)

    while True:
        try:
            # Reload settings each cycle (in case changed via web)
            Config.apply_settings()

            # Main check
            spotify_service.check_and_autoplay()

            # Log current state
            status = spotify_service.get_status()
            if status.get('playback'):
                pb = status['playback']
                state = "AUTOPLAY" if spotify_service.autoplay_mode else "USER"
                logger.info(f"[{state}] {pb['artist']} - {pb['track']} on {pb['device']}")
            elif status.get('stopped_since_minutes'):
                logger.info(f"[STOPPED] for {status['stopped_since_minutes']} min (trigger at {status['idle_minutes']} min)")
            else:
                logger.debug("No playback")

            time.sleep(check_interval)

        except KeyboardInterrupt:
            logger.info("Shutting down...")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(check_interval)


if __name__ == "__main__":
    main()
