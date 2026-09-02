"""
Text-To-Speech (TTS) Voice Alert Plugin.
Synthesizes local spoken audio warnings on speaker using pyttsx3 in non-blocking threads.
"""

import threading
import logging
from pathlib import Path
from typing import Optional
from modules.alerts.base import BaseAlertChannel

logger = logging.getLogger("TTSAlertChannel")


class TTSAlertChannel(BaseAlertChannel):
    """Offline Text-To-Speech voice alert channel plugin."""

    def __init__(self, message_text: str = "Warning! Unknown person detected at the smart home lock!"):
        self.message_text = message_text
        self._init_tts()

    def _init_tts(self):
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', 160)
            engine.setProperty('volume', 1.0)
            logger.info("Text-To-Speech engine initialized successfully.")
        except Exception as e:
            logger.warning(f"TTS Voice initialization notice: {e}")

    def _speak_worker(self, text: str):
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', 160)
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            logger.error(f"TTS Speech error: {e}")

    def send_alert(self, image_path: Optional[Path] = None, camera_name: str = "Front Door Camera") -> bool:
        voice_thread = threading.Thread(
            target=self._speak_worker,
            args=(self.message_text,),
            daemon=True
        )
        voice_thread.start()
        return True

    def close(self):
        pass
