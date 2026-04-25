"""
This script connects to a LEGO NXT brick and allows you to control it using the keyboard.
Controls:
- W / Up:       drive forward
- S / Down:     drive backward
- A / Left:     turn left
- D / Right:    turn right
- Space:        play tone
- Esc:          quit
Please configure the .nxt-python.conf first.
"""

import logging
from contextlib import nullcontext
from typing import Optional

import nxt.locator
from nxt.brick import Brick
from pynput import keyboard

from legobot.cameras import CameraStream
from legobot.controller import KeyboardController
from legobot.robots import NxtVehicle, VehicleBase

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(filename)s: %(message)s"
)
logger = logging.getLogger(__name__)

USE_BRICK = False
USE_CAMERA = True


def main():
    brick = initialize_brick()
    camera = initialize_cam()

    with (
        camera if camera else nullcontext(),
        brick if brick else nullcontext(),
    ):
        robot = NxtVehicle(brick) if brick else VehicleBase()
        controller = KeyboardController(robot, camera)
        listener = keyboard.Listener(
            on_press=controller.on_press,  # type: ignore
            on_release=controller.on_release,  # type: ignore
        )
        with listener:
            if camera:
                camera.join()
            else:
                listener.join()


def initialize_cam() -> Optional[CameraStream]:
    camera = None
    if USE_CAMERA:
        logger.info("Attempting to initialize camera stream...")
        try:
            camera = CameraStream()
        except Exception as e:
            logger.error(f"Initialization failed with error: {e}")
            logger.info("Continuing without camera stream.")
    else:
        logger.info("Camera stream is disabled. Continuing without camera.")
    return camera


def initialize_brick() -> Optional[Brick]:
    brick = None
    if USE_BRICK:
        logger.info("Attempting to connect to NXT brick via USB/Bluetooth...")
        try:
            brick = nxt.locator.find()
            logger.info("Connection to NXT brick established successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to NXT brick: {e}")
            logger.info("Continuing in simulation mode without physical brick.")
    else:
        logger.info("Running in simulation mode without physical brick.")
    return brick


if __name__ == "__main__":
    main()
