"""
MQTT Alert Channel Plugin.
Publishes real-time intruder notification messages over MQTT protocol to subscriber clients.
Supports TLS/SSL encryption and username/password authentication for security.
"""

import time
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional
import paho.mqtt.client as mqtt
from modules.alerts.base import BaseAlertChannel

logger = logging.getLogger("MQTTAlertChannel")


class MQTTAlertChannel(BaseAlertChannel):
    """MQTT notification channel plugin with TLS and Auth security support."""

    def __init__(
        self,
        broker: str = "test.mosquitto.org",
        port: int = 1883,
        topic: str = "smarthome/lock/alerts",
        use_tls: bool = False,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.use_tls = use_tls or port == 8883
        self.username = username
        self.password = password

        unique_id = f"SmartHome_Sender_{uuid.uuid4().hex[:8]}"
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=unique_id)
        self.mqtt_client.on_connect = self._on_connect
        self.is_connected = False

        # Apply security settings (Authentication & TLS)
        if self.username and self.password:
            self.mqtt_client.username_pw_set(self.username, self.password)
            logger.info("MQTT Client configured with username/password authentication.")

        if self.use_tls:
            import ssl
            self.mqtt_client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
            logger.info("MQTT Client configured with TLS/SSL transport encryption.")

        self._connect_mqtt()

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.is_connected = True
            logger.info(f"MQTT connected successfully to '{self.broker}:{self.port}' (TLS: {self.use_tls})")
        else:
            self.is_connected = False
            logger.warning(f"MQTT connection refused, return code: {rc}")

    def _connect_mqtt(self):
        try:
            logger.info(f"Connecting to MQTT Broker '{self.broker}:{self.port}' (TLS={self.use_tls})...")
            self.mqtt_client.connect_async(self.broker, self.port, keepalive=60)
            self.mqtt_client.loop_start()
            logger.info("MQTT Client loop started asynchronously.")
        except Exception as e:
            logger.warning(f"Failed to connect to MQTT Broker: {e}")
            self.is_connected = False

    def send_alert(self, image_path: Optional[Path] = None, camera_name: str = "Front Door Camera") -> bool:
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        image_name = str(Path(image_path).name) if image_path else "N/A"

        readable_message = (
            f"🚨 INTRUDER ALERT!\n"
            f"📷 Camera  : {camera_name}\n"
            f"🕐 Time    : {timestamp_str}\n"
            f"🖼 Image   : {image_name}\n"
            f"⚠ Warning  : Unknown person detected!"
        )

        try:
            if not self.is_connected:
                logger.info("Waiting for MQTT connection...")
                for _ in range(30):
                    if self.is_connected:
                        break
                    time.sleep(0.1)

            if self.is_connected:
                self.mqtt_client.publish(self.topic, readable_message, qos=1)
                logger.info(f"MQTT Alert Published to topic '{self.topic}':\n{readable_message}")
                return True
            else:
                logger.warning("MQTT not connected — alert skipped.")
                return False
        except Exception as e:
            logger.error(f"Failed to publish MQTT message: {e}")
            return False

    def close(self):
        try:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            logger.info("MQTT Client disconnected cleanly.")
        except Exception:
            pass
