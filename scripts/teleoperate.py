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

import nxt.locator
from pynput import keyboard

from legobot.controller import KeyboardController
from legobot.robots import NxtVehicle, VehicleBase

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(filename)s: %(message)s"
)
logger = logging.getLogger(__name__)

SIMULATION_MODE = True


def main():
    if SIMULATION_MODE:
        logger.info("Running in simulation mode without a physical brick.")

        robot = VehicleBase()
        controller = KeyboardController(robot)

        with keyboard.Listener(
            on_press=controller.on_press,  # type: ignore
            on_release=controller.on_release,  # type: ignore
        ) as listener:
            listener.join()

    else:
        logger.info("Attempting to connect to NXT brick via USB/Bluetooth...")

        try:
            with nxt.locator.find() as brick:
                logger.info("Successfully connected to NXT brick!")

                robot = NxtVehicle(brick)
                controller = KeyboardController(robot)

                with keyboard.Listener(
                    on_press=controller.on_press,  # type: ignore
                    on_release=controller.on_release,  # type: ignore
                ) as listener:
                    listener.join()

        except nxt.locator.BrickNotFoundError:
            logger.error(
                "Could not find the NXT brick. Check your Bluetooth connection."
            )


if __name__ == "__main__":
    main()
