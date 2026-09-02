"""
Configuration Schema & Validation Model.
Provides type safety, default values, security settings, and field documentation.
"""

from typing import Optional
from pydantic import BaseModel, Field


class CameraConfig(BaseModel):
    """Camera capture and stream configuration settings."""
    source: str = Field(
        default="0",
        description="Camera source index (e.g. '0' for default webcam, '1' for USB cam) or RTSP/HTTP URL"
    )
    frame_width: int = Field(
        default=640,
        ge=160,
        le=3840,
        description="Target frame capture width in pixels"
    )
    frame_height: int = Field(
        default=480,
        ge=120,
        le=2160,
        description="Target frame capture height in pixels"
    )
    fps: int = Field(
        default=30,
        ge=1,
        le=120,
        description="Target capture frames per second"
    )


class DetectionConfig(BaseModel):
    """Face detection & recognition confidence threshold settings."""
    confidence_threshold: float = Field(
        default=70.0,
        ge=0.0,
        le=500.0,
        description="LBPH distance threshold (distance <= threshold is treated as authorized match)"
    )
    unknown_cooldown_seconds: float = Field(
        default=5.0,
        ge=0.5,
        le=300.0,
        description="Anti-spam cooldown period in seconds between consecutive intruder alerts"
    )
    max_snapshot_retention_days: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Automatic privacy retention policy: delete local intruder snapshots older than N days"
    )


class MQTTConfig(BaseModel):
    """MQTT notification broker network and security settings."""
    broker: str = Field(
        default="test.mosquitto.org",
        description="MQTT broker hostname or IP address"
    )
    port: int = Field(
        default=1883,
        ge=1,
        le=65535,
        description="MQTT broker network port (1883 for TCP, 8883 for TLS)"
    )
    topic: str = Field(
        default="smarthome/lock/alerts",
        description="MQTT alert publish topic"
    )
    use_tls: bool = Field(
        default=False,
        description="Enable TLS/SSL encryption for MQTT transport security"
    )
    username: Optional[str] = Field(
        default=None,
        description="Optional username for authenticated MQTT brokers"
    )
    password: Optional[str] = Field(
        default=None,
        description="Optional password for authenticated MQTT brokers"
    )


class AlertConfig(BaseModel):
    """Alert channel configuration toggles."""
    enable_voice_alert: bool = Field(
        default=True,
        description="Toggle text-to-speech audio warning voice synthesizer"
    )
    mqtt: MQTTConfig = Field(default_factory=MQTTConfig)


class AppConfig(BaseModel):
    """Master Application Settings Container."""
    camera: CameraConfig = Field(default_factory=CameraConfig)
    detection: DetectionConfig = Field(default_factory=DetectionConfig)
    alerts: AlertConfig = Field(default_factory=AlertConfig)
