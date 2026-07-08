import logging
import threading
import time
from pathlib import Path
from typing import Optional, Union

import cv2

from legobot.robots import VehicleBase

logger = logging.getLogger(__name__)


class LiveCapture:
    """
    A class that handles live camera capture using OpenCV.
    Captures the stream from an attached camera, such as a webcam or a Wi-Fi camera.
    """

    def __init__(self, camera_source: Union[int, str], flip_frame: bool = False):
        """
        Initialize the live capture.

        Args:
            camera_source: The source of the camera (local index or URL).
            flip_frame: Whether to flip the captured frame horizontally.

        Raises:
            ValueError: If the camera stream cannot be opened.
        """
        self.cam_source = camera_source
        self.flip_frame = flip_frame
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
                    10000,
                    cv2.CAP_PROP_READ_TIMEOUT_MSEC,
                    2000,
                ],
            )

        # Set video capture property for buffering
        capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if not capture.isOpened():
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
            if ret:
                with self.frame_lock:
                    if self.flip_frame:
                        frame = cv2.flip(frame, 1)
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
        robot: Optional[VehicleBase] = None,
        save_path: Optional[Path] = None,
        fps: int = 25,
        main_width: int = 960,
        main_height: int = 720,
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
        self.robot = robot
        self.main_cap = main_capture
        self.main_width = main_width
        self.main_height = main_height
        self.opt_cap = opt_capture

        self.writer = None
        self.thread = None
        self.started = False
        self.stop_event = threading.Event()
        self.started_lock = threading.Lock()

    def compose_frame(self) -> Optional[cv2.typing.MatLike]:
        """
        Compose the main frame, the optional picture-in-picture frame, and the optional robot action.

        Returns:
            The composed frame, or None if the main frame is not available.
        """
        composed_frame = self.main_cap.get_frame()
        if composed_frame is not None:
            composed_frame = cv2.resize(
                composed_frame, (self.main_width, self.main_height)
            )
            self.add_opt_frame(composed_frame)
            self.add_robot_action_text(composed_frame)
        return composed_frame

    def add_opt_frame(self, frame: cv2.typing.MatLike):
        if self.opt_cap:
            opt_frame = self.opt_cap.get_frame()
            if opt_frame is not None:
                # Set optional frame as picture-in-picture
                opt_width = self.main_width // 4
                opt_height = self.main_height // 4
                opt_frame = cv2.resize(opt_frame, (opt_width, opt_height))
                frame[0:opt_height, 0:opt_width] = opt_frame

                # Draw a border around the picture-in-picture frame
                cv2.rectangle(
                    frame,
                    (0, 0),
                    (opt_width, opt_height),
                    (0, 0, 0),
                    2,
                )

    def add_robot_action_text(self, frame: cv2.typing.MatLike):
        if self.robot:
            text = self.robot.current_action.name
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 2
            thickness = 4

            # Padding around the text
            pad_x = 10
            pad_y = 10

            # Get text size
            (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, thickness)

            # Coordinates for bottom-left corner
            x = 0
            y = self.main_height

            # Rectangle coordinates
            rect_x1 = x
            rect_y1 = y - text_h - 2 * pad_y
            rect_x2 = x + text_w + 2 * pad_x
            rect_y2 = y

            # Draw filled rectangle
            cv2.rectangle(
                frame,
                (rect_x1, rect_y1),
                (rect_x2, rect_y2),
                (0, 0, 0),
                -1,
            )

            # Text coordinates
            text_x = x + pad_x
            text_y = y - pad_y

            # Draw text
            cv2.putText(
                frame,
                text,
                (text_x, text_y),
                font,
                font_scale,
                (255, 255, 255),
                thickness,
                cv2.LINE_AA,
            )

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
            duration_ms = (end - start) * 1000
            wait_fps = max(1, int(1000 / self.fps - duration_ms))
            if cv2.waitKey(wait_fps) & 0xFF == 27:
                logger.info("Quit signal received. Stopping rendering...")
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
        logger.info("Started rendering. Press 'Esc' to quit.")

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
