"""
Haar Cascade Face Detector Implementation.
Uses OpenCV's Haar Cascade classifier to locate frontal face regions in frames.
"""

import cv2
import logging
import numpy as np
from pathlib import Path
from typing import List, Tuple
from modules.detectors.base import BaseDetector

logger = logging.getLogger("HaarDetector")


class HaarDetector(BaseDetector):
    """Haar Cascade face detector implementation."""

    def __init__(self, cascade_path: Path = None):
        if cascade_path and Path(cascade_path).exists():
            self.cascade_file = Path(cascade_path)
        else:
            self.cascade_file = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"

        self.face_cascade = cv2.CascadeClassifier(str(self.cascade_file))
        if self.face_cascade.empty():
            logger.error(f"Failed to load Haar Cascade XML from: {self.cascade_file}")
        else:
            logger.info(f"Loaded Haar Cascade Classifier from: {self.cascade_file}")

    def detect(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        if frame is None or self.face_cascade.empty():
            return []

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detected_faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(50, 50)
        )
        return [(int(x), int(y), int(w), int(h)) for (x, y, w, h) in detected_faces]
