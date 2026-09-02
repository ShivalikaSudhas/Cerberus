"""
Abstract Base Class for Face Recognizers.
Subclass this to implement new recognition backends (e.g. LBPH, FaceNet, ArcFace, Dlib).
"""

from abc import ABC, abstractmethod
import numpy as np
from typing import Tuple, Dict


class BaseRecognizer(ABC):
    """Abstract Base Class defining the contract for all face recognizer backends."""

    @abstractmethod
    def predict(self, face_roi: np.ndarray) -> Tuple[int, float]:
        """
        Predicts identity for a grayscale cropped face region.

        Args:
            face_roi (np.ndarray): Grayscale cropped face image matrix.

        Returns:
            Tuple[int, float]: (label_id, distance_score)
        """
        pass

    @abstractmethod
    def load_model(self) -> bool:
        """Loads trained weights and label mapping dictionary."""
        pass

    @abstractmethod
    def train(self, faces: list, labels: list) -> bool:
        """
        Trains model weights on provided face samples and integer label IDs.

        Args:
            faces (list): List of grayscale face ROI matrices.
            labels (list): List of corresponding integer label IDs.

        Returns:
            bool: True if training succeeded, False otherwise.
        """
        pass

    @property
    @abstractmethod
    def label_map(self) -> Dict[int, str]:
        """Returns map of label ID -> person name string."""
        pass

    @property
    @abstractmethod
    def is_trained(self) -> bool:
        """Returns True if model weights are loaded and ready."""
        pass
