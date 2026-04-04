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
from legobot.nxt_robots import Vehicle
from legobot.controller import KeyboardController
import nxt.locator

from pynput import keyboard

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(filename)s: %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Attempting to connect to NXT brick via USB/Bluetooth...")

    try:
        with nxt.locator.find() as brick:
            logger.info("Successfully connected to NXT brick!")

            robot = Vehicle(brick)
            controller = KeyboardController(robot)

            with keyboard.Listener(
                on_press=controller.on_press, on_release=controller.on_release
            ) as listener:
                listener.join()

    except nxt.locator.BrickNotFoundError:
        logger.error(
            "ERROR: Could not find the NXT brick. Check your Bluetooth connection."
        )


if __name__ == "__main__":
    main()
