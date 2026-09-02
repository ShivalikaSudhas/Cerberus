"""
Centralized Configuration Loader & Path Manager.
Loads settings from .env file and validates them using Pydantic AppConfig.
Fails gracefully with instructions if .env is missing.
"""

import sys
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger("Settings")

# Base Project Paths (Relative to project root via pathlib)
BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset"
INTRUDERS_DIR = BASE_DIR / "intruders"
CCTV_STREAMS_DIR = BASE_DIR / "cctv_streams"
MODELS_DIR = BASE_DIR / "models"
ENV_FILE = BASE_DIR / ".env"

# Ensure essential directories exist
for folder in [DATASET_DIR, INTRUDERS_DIR, CCTV_STREAMS_DIR, MODELS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Graceful check for missing .env file
if not ENV_FILE.exists():
    print("\n" + "=" * 70)
    print("❌ ERROR: Configuration file '.env' not found!")
    print(f"   Expected location: {ENV_FILE}")
    print("\n👉 Please create your '.env' file by copying '.env.example':")
    print("   cp .env.example .env")
    print("=" * 70 + "\n")
    sys.exit(1)

# Load environment configuration
load_dotenv(dotenv_path=ENV_FILE)

# Import Schema after environment check
from config.schema import AppConfig, CameraConfig, DetectionConfig, AlertConfig, MQTTConfig

# Parse Camera Source
raw_source = os.getenv("CAMERA_SOURCE", "0")
try:
    CAMERA_SOURCE = int(raw_source)
except ValueError:
    CAMERA_SOURCE = str(raw_source)

FRAME_WIDTH = int(os.getenv("FRAME_WIDTH", 640))
FRAME_HEIGHT = int(os.getenv("FRAME_HEIGHT", 480))
FPS = int(os.getenv("FPS", 30))

# MQTT Settings
MQTT_BROKER = os.getenv("MQTT_BROKER", "test.mosquitto.org")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "smarthome/lock/alerts")
MQTT_USE_TLS = os.getenv("MQTT_USE_TLS", "False").lower() in ("true", "1", "t") or MQTT_PORT == 8883
MQTT_USERNAME = os.getenv("MQTT_USERNAME", None) or None
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", None) or None

# Detection & Alert Settings
UNKNOWN_COOLDOWN_SECONDS = float(os.getenv("UNKNOWN_COOLDOWN_SECONDS", 5.0))
LBPH_CONFIDENCE_THRESHOLD = float(os.getenv("LBPH_CONFIDENCE_THRESHOLD", 70.0))
CONFIDENCE_THRESHOLD = LBPH_CONFIDENCE_THRESHOLD
MAX_SNAPSHOT_RETENTION_DAYS = int(os.getenv("MAX_SNAPSHOT_RETENTION_DAYS", 30))

# Voice Notification Toggle
ENABLE_VOICE_ALERT = os.getenv("ENABLE_VOICE_ALERT", "True").lower() in ("true", "1", "t")

# Validated Pydantic AppConfig Object
CONFIG = AppConfig(
    camera=CameraConfig(
        source=str(CAMERA_SOURCE),
        frame_width=FRAME_WIDTH,
        frame_height=FRAME_HEIGHT,
        fps=FPS,
    ),
    detection=DetectionConfig(
        confidence_threshold=LBPH_CONFIDENCE_THRESHOLD,
        unknown_cooldown_seconds=UNKNOWN_COOLDOWN_SECONDS,
        max_snapshot_retention_days=MAX_SNAPSHOT_RETENTION_DAYS,
    ),
    alerts=AlertConfig(
        enable_voice_alert=ENABLE_VOICE_ALERT,
        mqtt=MQTTConfig(
            broker=MQTT_BROKER,
            port=MQTT_PORT,
            topic=MQTT_TOPIC,
            use_tls=MQTT_USE_TLS,
            username=MQTT_USERNAME,
            password=MQTT_PASSWORD,
        ),
    ),
)
