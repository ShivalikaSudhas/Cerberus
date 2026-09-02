"""
Face Detectors Package.
Provides swappable face detection plugins implementing BaseDetector.
"""

from modules.detectors.base import BaseDetector
from modules.detectors.haar_detector import HaarDetector

__all__ = ["BaseDetector", "HaarDetector"]
