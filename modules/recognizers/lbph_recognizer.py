"""
LBPH (Local Binary Patterns Histograms) Face Recognizer Implementation.
Uses OpenCV's LBPHFaceRecognizer for lightweight, fast face matching.
"""

import cv2
import json
import logging
import numpy as np
from pathlib import Path
from typing import Tuple, Dict
from modules.recognizers.base import BaseRecognizer

logger = logging.getLogger("LBPHRecognizer")


class LBPHRecognizer(BaseRecognizer):
    """LBPH face recognizer implementation."""

    def __init__(self, models_dir: Path = None):
        base_path = Path(__file__).resolve().parent.parent.parent
        self.models_dir = Path(models_dir) if models_dir else base_path / "models"
        self.model_yml_path = self.models_dir / "trained_lbph.yml"
        self.labels_json_path = self.models_dir / "labels.json"

        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self._label_map: Dict[int, str] = {}
        self._is_trained: bool = False

        self.load_model()

    @property
    def label_map(self) -> Dict[int, str]:
        return self._label_map

    @property
    def is_trained(self) -> bool:
        return self._is_trained

    def load_model(self) -> bool:
        if not self.model_yml_path.exists() or not self.labels_json_path.exists():
            logger.warning(f"Model files ('trained_lbph.yml' / 'labels.json') not found in {self.models_dir}.")
            self._is_trained = False
            return False

        try:
            try:
                self.recognizer.read(str(self.model_yml_path))
            except AttributeError:
                self.recognizer.load(str(self.model_yml_path))

            with open(self.labels_json_path, 'r', encoding='utf-8') as f:
                raw_labels = json.load(f)
                self._label_map = {int(k): v for k, v in raw_labels.items()}

            self._is_trained = True
            logger.info(f"Instant Load: LBPH Model & Labels loaded from {self.model_yml_path.name}! ({len(self._label_map)} user(s))")
            return True
        except Exception as e:
            logger.error(f"Failed to load trained LBPH model file: {e}")
            self._is_trained = False
            return False

    def predict(self, face_roi: np.ndarray) -> Tuple[int, float]:
        if not self._is_trained or face_roi is None:
            return -1, 999.0
        label_id, dist = self.recognizer.predict(face_roi)
        return label_id, round(dist, 1)

    def train(self, faces: list, labels: list) -> bool:
        if not faces or not labels:
            logger.error("No valid face samples provided for training.")
            return False

        try:
            self.models_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Training LBPH Model on {len(faces)} face region(s)...")
            self.recognizer.train(faces, np.array(labels))

            try:
                self.recognizer.save(str(self.model_yml_path))
            except AttributeError:
                self.recognizer.write(str(self.model_yml_path))

            self._is_trained = True
            logger.info(f"LBPH model successfully trained and saved to {self.model_yml_path}")
            return True
        except Exception as e:
            logger.error(f"LBPH training error: {e}")
            return False
