"""
Quick NXT Bluetooth connection test using nxt-python.

Uses motors on ports A and C to drive forward, backward, and turn left, right.

Please configure the .nxt-python.conf first.
"""

import logging
import time

import nxt.locator
from nxt.motor import Motor, Port

logging.basicConfig(level=logging.DEBUG)

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
        print("Found brick:", brick.get_device_info()[0])

        left_motor = brick.get_motor(Port.C)
        right_motor = brick.get_motor(Port.A)

        print("Driving forward")
        drive(left_motor, right_motor, POWER, POWER, DURATION)

        print("Driving backward")
        drive(left_motor, right_motor, -POWER, -POWER, DURATION)

        print("Turning left")
        drive(left_motor, right_motor, -POWER, POWER, DURATION)

        print("Turning right")
        drive(left_motor, right_motor, POWER, -POWER, DURATION)

        print("Testing completed")
        brick.play_tone(440, 250)


if __name__ == "__main__":
    main()
