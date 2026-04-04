from nxt.brick import Brick
from nxt.motor import Motor, Port
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Vehicle:
    def __init__(self, brick: Brick) -> None:
        self.brick: Brick = brick
        self.left_motor: Motor = brick.get_motor(Port.C)
        self.right_motor: Motor = brick.get_motor(Port.A)
        # Default power level for all movements, should be between 64 and 128
        self.power: int = 100

    def execute_command(self, action: Optional[str]) -> None:
        """Interprets the logical action and drives the motors."""
        if action == "forward":
            logger.info("--> Robot moving FORWARD")
            self.left_motor.run(self.power)
            self.right_motor.run(self.power)

        elif action == "backward":
            logger.info("--> Robot moving BACKWARD")
            self.left_motor.run(-self.power)
            self.right_motor.run(-self.power)

        elif action == "left":
            logger.info("--> Robot turning LEFT")
            self.left_motor.run(-self.power)
            self.right_motor.run(self.power)

        elif action == "right":
            logger.info("--> Robot turning RIGHT")
            self.left_motor.run(self.power)
            self.right_motor.run(-self.power)

        elif action == "space_action":
            logger.info("--> Robot playing TONE")
            self.left_motor.brake()
            self.right_motor.brake()
            self.brick.play_tone(440, 500)

        elif action is None:
            logger.info("--> Robot STOPPED")
            self.left_motor.brake()
            self.right_motor.brake()
