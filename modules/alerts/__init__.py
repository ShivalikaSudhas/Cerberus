"""
Alert Channels Package.
Provides swappable alert channel plugins implementing BaseAlertChannel.
"""

from modules.alerts.base import BaseAlertChannel
from modules.alerts.mqtt_alert import MQTTAlertChannel
from modules.alerts.tts_alert import TTSAlertChannel

__all__ = ["BaseAlertChannel", "MQTTAlertChannel", "TTSAlertChannel"]
