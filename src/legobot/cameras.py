import logging
import os
import threading
from typing import Optional, Union

import cv2
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class CameraStream:
    """
    A class that handles live camera streaming using OpenCV.
    Supports both local camera and IP-based wireless cameras.
    """

    def __init__(self, camera_source: Optional[int] = None):
        """
        Initialize the camera stream.

        Args:
            camera_source: Local camera index. If None, it will try to read from the CAMERA_URL environment variable or default to 0.
        """
        self.camera_source = camera_source or os.getenv("CAMERA_URL", 0)
        self.cap = self._open_capture(self.camera_source)
        self.window_name = "Camera Stream"
        self.frame = None

        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.render_thread = threading.Thread(target=self._render_loop, daemon=True)
        self.stop_event = threading.Event()
        self.frame_lock = threading.Lock()

    def get_frame(self) -> Optional[cv2.typing.MatLike]:
        """
        Get the latest captured frame.

        Returns:
            The latest frame if available, otherwise None.
        """
        with self.frame_lock:
            return self.frame

    def _open_capture(self, camera_source: Union[int, str]) -> cv2.VideoCapture:
        """
        Open the video capture based on the camera source.

        Args:
            camera_source: The source of the camera (local index or IP address).

        Returns:
            The video capture object.

        Raises:
            ValueError: If the camera stream cannot be opened.
        """
        if isinstance(camera_source, int):
            capture = cv2.VideoCapture(camera_source)
        else:
            # Set video capture properties for timeouts
            capture = cv2.VideoCapture(
                camera_source,
                apiPreference=cv2.CAP_FFMPEG,
                params=[
                    cv2.CAP_PROP_OPEN_TIMEOUT_MSEC,
                    5000,
                    cv2.CAP_PROP_READ_TIMEOUT_MSEC,
                    2000,
                ],
            )

        # Set video capture property for buffering
        capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if capture.isOpened():
            logger.info(
                f"Camera stream opened successfully from source: {camera_source}"
            )
        else:
            raise ValueError(
                f"Failed to open camera stream, source {camera_source} is not reachable."
            )
        return capture

    def _capture_loop(self) -> None:
        """
        Capture frames in a background thread and keep the latest frame available.
        """
        while not self.stop_event.is_set():
            ret, frame = self.cap.read()
            if not ret:
                logger.error("Failed to read frame from camera.")
                continue
            with self.frame_lock:
                self.frame = frame

    def _render_loop(self) -> None:
        """
        Run the rendering loop in the main thread until stop_event is set.
        """
        while not self.stop_event.is_set():
            frame = self.get_frame()

            if frame is not None:
                frame = cv2.resize(frame, (640, 480))
                if self.camera_source == 0:
                    frame = cv2.flip(frame, 1)
                cv2.imshow(self.window_name, frame)
                if cv2.waitKey(20) & 0xFF == ord("q"):
                    logger.info("Quit signal received. Stopping camera stream.")
                    self.stop_event.set()

    def join(self) -> None:
        self.render_thread.join()

    def start(self) -> None:
        self.capture_thread.start()
        self.render_thread.start()
        logger.info("Camera stream started.")

    def stop(self) -> None:
        self.stop_event.set()
        self.capture_thread.join(timeout=2)
        self.render_thread.join(timeout=2)
        self.cap.release()
        cv2.destroyAllWindows()
        logger.info("Camera stream stopped.")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
