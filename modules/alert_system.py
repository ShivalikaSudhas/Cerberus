"""
Modular Alert Dispatcher & Notification System.
Dispatches alerts to multiple registered BaseAlertChannel plugins (e.g. MQTT, TTS, Telegram).
"""

import time
import logging
from pathlib import Path
from typing import List, Optional
from modules.alerts import BaseAlertChannel, MQTTAlertChannel, TTSAlertChannel

logger = logging.getLogger("AlertSystem")


class AlertSystem:
    """
    Manages real-time alert notifications across swappable alert channel plugins.
    Preserves exact API contract for main surveillance loop.
    """

    def __init__(
        self,
        broker: str = "test.mosquitto.org",
        port: int = 1883,
        topic: str = "smarthome/lock/alerts",
        enable_voice: bool = True,
        cooldown: float = 5.0,
        channels: Optional[List[BaseAlertChannel]] = None
    ):
        self.cooldown = cooldown
        self.last_alert_time = 0.0

        if channels is not None:
            self.channels = channels
        else:
            self.channels = []
            # Default Channel 1: MQTT Publisher
            self.channels.append(MQTTAlertChannel(broker=broker, port=port, topic=topic))
            # Default Channel 2: TTS Voice Audio Alert
            if enable_voice:
                self.channels.append(TTSAlertChannel())

    def trigger_intruder_alert(self, image_path: Optional[Path] = None, camera_name: str = "Front Door Camera") -> bool:
        """Triggers intruder alert across all registered alert channels if cooldown has passed."""
        current_time = time.time()
        if (current_time - self.last_alert_time) < self.cooldown:
            return False  # Cooldown active

        self.last_alert_time = current_time
        logger.info(f"Triggering intruder alert across {len(self.channels)} channel(s)...")

        success_count = 0
        for channel in self.channels:
            try:
                if channel.send_alert(image_path=image_path, camera_name=camera_name):
                    success_count += 1
            except Exception as e:
                logger.error(f"Alert channel dispatch error ({channel.__class__.__name__}): {e}")

        return success_count > 0

    def close(self):
        """Disconnects all alert channels cleanly."""
        for channel in self.channels:
            try:
                channel.close()
            except Exception:
                pass
        logger.info("All alert channels closed cleanly.")
