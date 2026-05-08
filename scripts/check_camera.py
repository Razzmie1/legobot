"""
Quick camera connection check.

Please set the CAMERA_URL in the .env file first, otherwise it will use the default camera source 0.
"""

import logging
import os

import cv2
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(filename)s: %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()


def main():
    camera_url = os.getenv("CAMERA_URL", 0)

    logger.info(f"Opening camera stream: {camera_url}")
    if isinstance(camera_url, int):
        cap = cv2.VideoCapture(camera_url)
    else:
        # Set video capture properties for timeouts
        cap = cv2.VideoCapture(
            camera_url,
            apiPreference=cv2.CAP_FFMPEG,
            params=[
                cv2.CAP_PROP_OPEN_TIMEOUT_MSEC,
                5000,
                cv2.CAP_PROP_READ_TIMEOUT_MSEC,
                2000,
            ],
        )

    if not cap.isOpened():
        logger.error("Unable to open camera stream. Check CAMERA_URL and connection.")
        return

    logger.info("Press 'q' to close the stream.")
    while True:
        ret, frame = cap.read()
        if not ret:
            logger.error("Failed to read frame from camera stream.")
            break

        cv2.imshow("Camera Check", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    logger.info("Camera stream closed.")


if __name__ == "__main__":
    main()
