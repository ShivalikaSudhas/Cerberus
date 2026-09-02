"""
Abstract Base Class for Face Detectors.
Subclass this to implement new face detection backends (e.g. Haar Cascade, YuNet, OpenCV DNN, MTCNN).
"""

from abc import ABC, abstractmethod
import numpy as np
from typing import List, Tuple


class BaseDetector(ABC):
    """Abstract Base Class defining the contract for all face detector backends."""

    @abstractmethod
    def detect(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detects faces in a BGR image frame.

        Args:
            frame (np.ndarray): Input BGR image matrix.

        Returns:
            List[Tuple[int, int, int, int]]: List of bounding boxes as (x, y, width, height).
        """
        pass
