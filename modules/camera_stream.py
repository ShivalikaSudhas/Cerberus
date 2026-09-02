import os
import cv2
import time
import logging
from dotenv import load_dotenv

# Load environment configuration from .env
load_dotenv()

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(name)s] %(message)s')
logger = logging.getLogger("CameraStream")

class CameraStream:
    """
    Class-based Camera Stream Manager.
    Supports:
    - Local webcam by index (0, 1, 2...)
    - RTSP / HTTP network video stream URLs (IP Cameras / CCTV)
    - Raspberry Pi CSI camera placeholder (rpicam-vid / libcamera RTSP stream stub)
    - Configurable resolution & auto-reconnect with exponential backoff delay.
    """
    def __init__(self, source=None, width=None, height=None, fps=None):
        # Load from parameters or .env configuration defaults
        raw_source = source if source is not None else os.getenv("CAMERA_SOURCE", "0")
        
        # Parse source as int for USB index, or keep as string for RTSP/HTTP URL
        try:
            self.source = int(raw_source)
        except ValueError:
            self.source = str(raw_source)

        self.width = width if width is not None else int(os.getenv("FRAME_WIDTH", 640))
        self.height = height if height is not None else int(os.getenv("FRAME_HEIGHT", 480))
        self.fps = fps if fps is not None else int(os.getenv("FPS", 30))

        self.cap = None
        self.is_running = False
        self.reconnect_attempts = 0
        self.max_backoff_delay = 10.0  # Seconds cap for exponential backoff

        self._connect()

    def _connect(self):
        """Initializes VideoCapture for webcam, RTSP, or Raspberry Pi CSI RTSP stub."""
        logger.info(f"Initializing camera stream (Source: {self.source})...")

        # Raspberry Pi CSI Camera RTSP Stub Check
        if isinstance(self.source, str) and ("rpicam" in self.source or "libcamera" in self.source):
            logger.info("Raspberry Pi CSI Camera stream stub detected (libcamera/rpicam-vid RTSP).")

        if isinstance(self.source, int):
            # Windows DirectShow or standard V4L2 USB camera backend
            backend = cv2.CAP_DSHOW if os.name == 'nt' else cv2.CAP_ANY
            self.cap = cv2.VideoCapture(self.source, backend)
        else:
            # RTSP / HTTP URL Stream
            self.cap = cv2.VideoCapture(self.source)

        if self.cap and self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            self.is_running = True
            self.reconnect_attempts = 0
            logger.info(f"Camera stream connected ({self.width}x{self.height} @ {self.fps} FPS).")
        else:
            logger.warning(f"Unable to open camera source '{self.source}'. Stream unavailable.")
            self.is_running = False

    def get_frame(self):
        """
        Reads a frame from the stream.
        If stream drops or disconnects, applies exponential backoff delay and retries.
        Returns: (success: bool, frame: np.ndarray or None)
        """
        if not self.is_running or self.cap is None:
            self._handle_reconnect()
            if not self.is_running:
                return False, None

        ret, frame = self.cap.read()

        if not ret or frame is None:
            logger.warning("Stream disconnected or frame drop detected. Initiating auto-reconnect...")
            self.is_running = False
            self._handle_reconnect()
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()

        return ret, frame

    def _handle_reconnect(self):
        """Calculates exponential backoff delay and attempts reconnection."""
        self.reconnect_attempts += 1
        backoff_delay = min(2.0 ** self.reconnect_attempts, self.max_backoff_delay)
        logger.info(f"Reconnecting attempt #{self.reconnect_attempts} in {backoff_delay:.1f}s...")
        time.sleep(backoff_delay)
        self._connect()

    def release(self):
        """Releases camera hardware and OpenCV windows cleanly."""
        self.is_running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
            logger.info("Camera resources released successfully.")
        cv2.destroyAllWindows()
