import cv2
import logging
from datetime import datetime
from pathlib import Path
from modules.camera_stream import CameraStream
from modules.face_engine import FaceEngine
from modules.alert_system import AlertSystem
from modules.alerts.mqtt_alert import MQTTAlertChannel
from modules.alerts.tts_alert import TTSAlertChannel
from modules.storage import StorageManager
from config.settings import (
    INTRUDERS_DIR, UNKNOWN_COOLDOWN_SECONDS, ENABLE_VOICE_ALERT,
    MQTT_BROKER, MQTT_PORT, MQTT_TOPIC, MQTT_USE_TLS,
    MQTT_USERNAME, MQTT_PASSWORD, MAX_SNAPSHOT_RETENTION_DAYS,
    LBPH_CONFIDENCE_THRESHOLD
)

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(name)s] %(message)s')
logger = logging.getLogger("MainSurveillance")


def main():
    logger.info("Starting Smart Home Surveillance System (Camera + Face Recognition + Secure Alerts)...")

    # 1. Initialize Camera Stream Manager
    camera = CameraStream()

    # 2. Initialize Face Detection & Recognition Engine
    face_engine = FaceEngine(threshold=LBPH_CONFIDENCE_THRESHOLD)

    # 3. Initialize Local Snapshot Storage Manager with Privacy Retention Policy
    storage = StorageManager(INTRUDERS_DIR, retention_days=MAX_SNAPSHOT_RETENTION_DAYS)

    # 4. Initialize Alert Channels (MQTT with TLS/Auth + TTS Voice)
    channels = []
    channels.append(MQTTAlertChannel(
        broker=MQTT_BROKER,
        port=MQTT_PORT,
        topic=MQTT_TOPIC,
        use_tls=MQTT_USE_TLS,
        username=MQTT_USERNAME,
        password=MQTT_PASSWORD
    ))
    if ENABLE_VOICE_ALERT:
        channels.append(TTSAlertChannel())

    alert_system = AlertSystem(cooldown=UNKNOWN_COOLDOWN_SECONDS, channels=channels)

    logger.info(f"MQTT Publisher active on '{MQTT_BROKER}:{MQTT_PORT}' (TLS={MQTT_USE_TLS}) topic '{MQTT_TOPIC}'.")
    logger.info("Live feed active. Press 'q' to Quit, 'r' to Retrain, 's' to Save Snapshot.")

    try:
        while True:
            ret, frame = camera.get_frame()
            if not ret or frame is None:
                continue

            results = face_engine.detect_and_recognize(frame)
            has_unknown = False

            for (x, y, w, h, name, is_match, distance) in results:
                if is_match:
                    color = (0, 255, 0)  # Green for Authorized Match
                    label = f"{name} (dist: {distance})"
                else:
                    color = (0, 0, 255)  # Red for Unknown Face
                    label = f"Unknown (dist: {distance})"
                    has_unknown = True

                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                cv2.rectangle(frame, (x, y - 28), (x + w, y), color, -1)
                cv2.putText(frame, label, (x + 5, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

            if has_unknown:
                image_path = storage.save_intruder_frame(frame)
                alert_system.trigger_intruder_alert(image_path=image_path)

            cv2.putText(frame, "Keys: [q] Quit | [r] Retrain Dataset | [s] Save Snapshot", 
                        (10, frame.shape[0] - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

            cv2.imshow("Smart Home Surveillance - Camera & Face Detection", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                logger.info("Quit key ('q') pressed. Exiting...")
                break
            elif key == ord('r'):
                logger.info("Retrain key ('r') pressed.")
                face_engine.retrain()
            elif key == ord('s'):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                snapshot_path = INTRUDERS_DIR / f"snapshot_{timestamp}.jpg"
                cv2.imwrite(str(snapshot_path), frame)
                logger.info(f"Manual snapshot saved to disk: {snapshot_path}")

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received. Stopping...")
    finally:
        camera.release()
        alert_system.close()
        logger.info("Camera and Alert System released cleanly.")


if __name__ == "__main__":
    main()
