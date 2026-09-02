"""
Decoupled Face Detection & Recognition Engine Orchestrator.
Orchestrates swappable BaseDetector and BaseRecognizer plugins.
"""

import logging
from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np

from modules.detectors import BaseDetector, HaarDetector
from modules.recognizers import BaseRecognizer, LBPHRecognizer

logger = logging.getLogger("FaceEngine")


class FaceEngine:
    """
    Modular Face Detection & Recognition Engine.
    Orchestrates detector and recognizer plugins while preserving exact API contract.
    """

    def __init__(
        self,
        models_dir: Optional[Path] = None,
        threshold: float = 70.0,
        detector: Optional[BaseDetector] = None,
        recognizer: Optional[BaseRecognizer] = None
    ):
        base_path = Path(__file__).resolve().parent.parent
        self.models_dir = Path(models_dir) if models_dir else base_path / "models"
        self.threshold = threshold

        # Plug-in Detector (default: HaarDetector)
        self.detector = detector if detector else HaarDetector(
            cascade_path=self.models_dir / "haarcascade_frontalface_default.xml"
        )

        # Plug-in Recognizer (default: LBPHRecognizer)
        self.recognizer = recognizer if recognizer else LBPHRecognizer(
            models_dir=self.models_dir
        )

        # Auto-train fallback if weights missing
        if not self.recognizer.is_trained:
            self._attempt_auto_train()

    @property
    def is_trained(self) -> bool:
        return self.recognizer.is_trained

    @property
    def label_map(self) -> dict:
        return self.recognizer.label_map

    def _attempt_auto_train(self) -> bool:
        logger.info("Pre-trained model weights not found. Attempting auto-training from dataset...")
        try:
            from train_model import train_standalone
            if train_standalone():
                return self.recognizer.load_model()
        except Exception as e:
            logger.error(f"Auto-train error: {e}")
        return False

    def load_model(self) -> bool:
        return self.recognizer.load_model()


    def retrain(self) -> bool:
        logger.info("Retrain requested. Launching dataset trainer...")
        try:
            from train_model import train_standalone
            if train_standalone():
                return self.recognizer.load_model()
        except Exception as e:
            logger.error(f"Retrain execution error: {e}")
        return False

    def detect_and_recognize(self, frame: np.ndarray) -> List[Tuple[int, int, int, int, str, bool, float]]:
        """
        Detects faces in frame and recognizes identity.
        Matching logic: distance <= threshold is treated as confident match, else 'Unknown'.

        Returns:
            List of tuples: (x, y, w, h, name, is_match, distance)
        """
        if frame is None:
            return []

        # 1. Detect faces using configured detector plugin
        detected_boxes = self.detector.detect(frame)
        if not detected_boxes:
            return []

        gray = cv2_convert_gray(frame)
        results = []

        # 2. Recognize faces using configured recognizer plugin
        for (x, y, w, h) in detected_boxes:
            face_roi = gray[y:y+h, x:x+w]
            name = "Unknown"
            is_match = False
            distance = 999.0

            if self.recognizer.is_trained:
                label_id, dist = self.recognizer.predict(face_roi)
                distance = round(dist, 1)

                if dist <= self.threshold and label_id in self.recognizer.label_map:
                    name = self.recognizer.label_map[label_id]
                    is_match = True

            results.append((x, y, w, h, name, is_match, distance))

        return results


def cv2_convert_gray(frame: np.ndarray) -> np.ndarray:
    import cv2
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
