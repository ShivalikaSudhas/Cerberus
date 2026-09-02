"""
Face Recognizers Package.
Provides swappable face recognition plugins implementing BaseRecognizer.
"""

from modules.recognizers.base import BaseRecognizer
from modules.recognizers.lbph_recognizer import LBPHRecognizer

__all__ = ["BaseRecognizer", "LBPHRecognizer"]
