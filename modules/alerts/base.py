"""
Abstract Base Class for Alert Notification Channels.
Subclass this to implement new notification outputs (e.g. MQTT, TTS, Telegram, Email, Webhook).
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class BaseAlertChannel(ABC):
    """Abstract Base Class defining the contract for all alert channels."""

    @abstractmethod
    def send_alert(self, image_path: Optional[Path] = None, camera_name: str = "Front Door Camera") -> bool:
        """
        Triggers alert message dispatch through this channel.

        Args:
            image_path (Optional[Path]): Path to captured intruder snapshot image.
            camera_name (str): Label of camera triggering the event.

        Returns:
            bool: True if alert dispatched successfully, False otherwise.
        """
        pass

    @abstractmethod
    def close(self):
        """Cleans up background threads, network sockets, or connections cleanly."""
        pass
