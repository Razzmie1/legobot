"""
Quick NXT Bluetooth connection test using nxt-python.

Uses motors on ports A and C to drive forward, backward, and turn left, right.

Please configure the .nxt-python.conf first.
"""

import logging
import time

import nxt.locator
from nxt.motor import Motor, Port

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(filename)s: %(message)s"
)
logger = logging.getLogger(__name__)

POWER = 100
DURATION = 1.0


def drive(
    left_motor: Motor,
    right_motor: Motor,
    left_power: int,
    right_power: int,
    duration: float,
) -> None:

    right_motor.run(right_power)
    left_motor.run(left_power)

    time.sleep(duration)

    right_motor.brake()
    left_motor.brake()


def main() -> None:
    with nxt.locator.find() as brick:
        logger.info(f"Found brick: {brick.get_device_info()[0]}")

        left_motor = brick.get_motor(Port.C)
        right_motor = brick.get_motor(Port.A)

        logger.info("Driving forward")
        drive(left_motor, right_motor, POWER, POWER, DURATION)

        logger.info("Driving backward")
        drive(left_motor, right_motor, -POWER, -POWER, DURATION)

        logger.info("Turning left")
        drive(left_motor, right_motor, -POWER, POWER, DURATION)

        logger.info("Turning right")
        drive(left_motor, right_motor, POWER, -POWER, DURATION)

        logger.info("Testing completed")
        brick.play_tone(440, 500)


if __name__ == "__main__":
    main()
