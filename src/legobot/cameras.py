import logging
from pathlib import Path
import threading
import time
from typing import Optional, Union

import cv2

logger = logging.getLogger(__name__)


class LiveCapture:
    """
    A class that handles live camera capture using OpenCV.
    Captures the stream from an attached camera, such as a webcam or a Wi-Fi camera.
    """

    def __init__(self, camera_source: Union[int, str]):
        """
        Initialize the live capture.

        Args:
            camera_source: The source of the camera (local index or URL).

        Raises:
            ValueError: If the camera stream cannot be opened.
        """
        self.cam_source = camera_source
        self.cap = self._open_capture()
        self.frame: Optional[cv2.typing.MatLike] = None
        self.thread = None
        self.started = False
        self.stop_event = threading.Event()
        self.frame_lock = threading.Lock()
        self.started_lock = threading.Lock()

    def _open_capture(self) -> cv2.VideoCapture:
        """
        Open the video capture based on the camera source.

        Args:
            camera_source: The source of the camera (local index or URL).

        Returns:
            The video capture object.

        Raises:
            ValueError: If the camera stream cannot be opened.
        """
        if isinstance(self.cam_source, int):
            capture = cv2.VideoCapture(self.cam_source)
        else:
            # Set video capture properties for timeouts
            capture = cv2.VideoCapture(
                self.cam_source,
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
                f"Camera capture opened successfully from source: {self.cam_source}"
            )
        else:
            raise ValueError(
                f"Failed to open camera capture from source: {self.cam_source}."
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
            else:
                with self.frame_lock:
                    self.frame = frame

    def get_frame(self) -> Optional[cv2.typing.MatLike]:
        """
        Get the latest captured frame.

        Returns:
            The latest captured frame, or None if no frame is available.
        """
        with self.frame_lock:
            return self.frame

    def join(self) -> None:
        if self.thread:
            self.thread.join()

    def start(self) -> None:
        with self.started_lock:
            if self.started:
                return
            self.started = True
            self.stop_event.clear()

        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        logger.info(f"Started camera capture from source: {self.cam_source}.")

    def stop(self) -> None:
        with self.started_lock:
            if not self.started:
                return
            self.started = False
            self.stop_event.set()

        if self.thread:
            self.thread.join(timeout=2)

        self.cap.release()
        logger.info(f"Stopped camera capture from source: {self.cam_source}.")


class LiveRender:
    """
    A class that handles live camera rendering using OpenCV.
    Renders the main capture stream and optionally an additional capture stream as a small picture-in-picture.
    """

    def __init__(
        self,
        main_capture: LiveCapture,
        opt_capture: Optional[LiveCapture] = None,
        save_path: Optional[Path] = None,
        fps: int = 50,
        main_width: int = 960,
        main_height: int = 720,
        opt_downscale_factor: int = 4,
    ):
        """
        Initialize the camera stream.

        Args:
            main_capture: The main camera capture object.
            opt_capture: The optional camera capture object.
        """

        self.window_name = "Camera Stream"
        self.fps = fps
        self.save_path = save_path
        self.main_cap = main_capture
        self.main_width = main_width
        self.main_height = main_height
        self.opt_cap = opt_capture
        self.opt_width = main_width // opt_downscale_factor
        self.opt_height = main_height // opt_downscale_factor

        self.writer = None
        self.thread = None
        self.started = False
        self.stop_event = threading.Event()
        self.started_lock = threading.Lock()

    def compose_frame(self) -> Optional[cv2.typing.MatLike]:
        """
        Compose the main frame and the optional picture-in-picture frame.

        Returns:
            The composed frame, or None if the main frame is not available.
        """
        composed_frame = self.main_cap.get_frame()
        if composed_frame is not None:
            composed_frame = cv2.resize(
                composed_frame, (self.main_width, self.main_height)
            )
            if self.main_cap.cam_source == 0:
                composed_frame = cv2.flip(composed_frame, 1)

            if self.opt_cap:
                opt_frame = self.opt_cap.get_frame()
                if opt_frame is not None:
                    opt_frame = cv2.resize(opt_frame, (self.opt_width, self.opt_height))
                    # Flip the local webcam feed for a more natural view
                    if self.opt_cap.cam_source == 0:
                        opt_frame = cv2.flip(opt_frame, 1)
                    composed_frame[0 : self.opt_height, 0 : self.opt_width] = opt_frame
                    # Draw a border around the picture-in-picture frame
                    cv2.rectangle(
                        composed_frame,
                        (0, 0),
                        (self.opt_width, self.opt_height),
                        (0, 0, 0),
                        2,
                    )
        return composed_frame

    def _render_loop(self) -> None:
        """
        Compose the frame and render it until 'Esc' is pressed.
        """
        while not self.stop_event.is_set():
            start = time.time()
            composed_frame = self.compose_frame()
            if composed_frame is not None:
                cv2.imshow(self.window_name, composed_frame)
                if self.writer:
                    self.writer.write(composed_frame)
            end = time.time()
            duration = int(end - start)
            wait_fps = max(1, 1000 // self.fps - duration)
            if cv2.waitKey(wait_fps) & 0xFF == 27:
                logger.info("Quit signal received. Stopping rendering.")
                self.stop_event.set()

    def join(self) -> None:
        if self.thread is not None:
            self.thread.join()

    def start(self) -> None:
        with self.started_lock:
            if self.started:
                return
            self.started = True
            self.stop_event.clear()

        self.main_cap.start()
        if self.opt_cap:
            self.opt_cap.start()

        if self.save_path:
            fourcc = cv2.VideoWriter.fourcc("m", "p", "4", "v")
            self.writer = cv2.VideoWriter(
                self.save_path, fourcc, self.fps, (self.main_width, self.main_height)
            )
        self.thread = threading.Thread(target=self._render_loop, daemon=True)
        self.thread.start()
        logger.info("Started rendering.")

    def stop(self) -> None:
        with self.started_lock:
            if not self.started:
                return
            self.started = False
            self.stop_event.set()

        self.main_cap.stop()
        if self.opt_cap:
            self.opt_cap.stop()
        if self.thread:
            self.thread.join(timeout=2)
        if self.writer:
            self.writer.release()
        cv2.destroyAllWindows()
        logger.info("Stopped rendering.")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
