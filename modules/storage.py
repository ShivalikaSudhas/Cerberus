"""
Storage Manager & Privacy Retention Engine.
Handles local snapshot persistence, CSV audit logging, and automatic snapshot deletion after N days.
"""

import cv2
import csv
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

logger = logging.getLogger("StorageManager")


class StorageManager:
    """
    Handles local file storage for intruder images and event audit logs.
    Includes privacy retention policy enforcement.
    """
    def __init__(self, intruders_dir: Path, retention_days: int = 30):
        self.intruders_dir = Path(intruders_dir)
        self.intruders_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.intruders_dir / "intruder_log.csv"
        self.retention_days = retention_days
        self._init_log_file()
        self.cleanup_old_snapshots()

    def _init_log_file(self):
        """Initializes CSV log file header if it doesn't exist."""
        if not self.log_file.exists():
            with open(self.log_file, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Image_Path", "Status", "Camera_Source"])

    def cleanup_old_snapshots(self) -> int:
        """
        Privacy Retention Policy:
        Deletes intruder JPEG snapshots older than `self.retention_days` days.
        """
        if self.retention_days <= 0:
            return 0

        now = time.time()
        cutoff = now - (self.retention_days * 86400)
        deleted_count = 0

        for img_path in self.intruders_dir.glob("*.jpg"):
            try:
                if img_path.stat().st_mtime < cutoff:
                    img_path.unlink()
                    deleted_count += 1
            except Exception as e:
                logger.warning(f"Failed to delete old snapshot '{img_path.name}': {e}")

        if deleted_count > 0:
            logger.info(f"Privacy retention policy enforced: Purged {deleted_count} intruder snapshot(s) older than {self.retention_days} days.")

        return deleted_count

    def save_intruder_frame(self, frame, camera_name: str = "Camera_0") -> Optional[Path]:
        """Saves current image frame to intruders directory and logs entry."""
        if frame is None:
            return None

        timestamp = datetime.now()
        filename = f"intruder_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
        file_path = self.intruders_dir / filename

        # Save image frame securely
        success = cv2.imwrite(str(file_path), frame)
        if success:
            logger.info(f"Intruder image saved: {file_path}")
            # Append entry to CSV log
            with open(self.log_file, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp.strftime('%Y-%m-%d %H:%M:%S'), str(file_path), "UNKNOWN_DETECTED", camera_name])
            return file_path
        else:
            logger.error("Failed to write intruder image to storage.")
            return None
