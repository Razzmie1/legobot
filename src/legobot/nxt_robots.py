import logging
from enum import Enum

from nxt.brick import Brick
from nxt.motor import Port

logger = logging.getLogger(__name__)


class VehicleBase:
    """
    Base class for vehicles which defines the interface and can be used for testing.
    """

    class Action(Enum):
        FORWARD = 1
        BACKWARD = 2
        LEFT = 3
        RIGHT = 4
        SPACE = 5
        STOP = 6

    def forward(self) -> Action:
        logger.info(f"Executed Action: {VehicleBase.Action.FORWARD.name}")
        return VehicleBase.Action.FORWARD

    def backward(self) -> Action:
        logger.info(f"Executed Action: {VehicleBase.Action.BACKWARD.name}")
        return VehicleBase.Action.BACKWARD

    def left(self) -> Action:
        logger.info(f"Executed Action: {VehicleBase.Action.LEFT.name}")
        return VehicleBase.Action.LEFT

    def right(self) -> Action:
        logger.info(f"Executed Action: {VehicleBase.Action.RIGHT.name}")
        return VehicleBase.Action.RIGHT

    def space(self) -> Action:
        logger.info(f"Executed Action: {VehicleBase.Action.SPACE.name}")
        return VehicleBase.Action.SPACE

    def stop(self) -> Action:
        logger.info(f"Executed Action: {VehicleBase.Action.STOP.name}")
        return VehicleBase.Action.STOP


class NxtVehicle(VehicleBase):
    """
    A vehicle implementation that controls a physical NXT robot using the nxt-python library.
    """

    def __init__(self, brick: Brick):
        self.brick = brick
        self.left_motor = brick.get_motor(Port.C)
        self.right_motor = brick.get_motor(Port.A)

        # Default power level for all movements, should be between 64 and 128
        self.power: int = 100

    def forward(self):
        self.left_motor.run(self.power)
        self.right_motor.run(self.power)
        return super().forward()

    def backward(self):
        self.left_motor.run(-self.power)
        self.right_motor.run(-self.power)
        return super().backward()

    def left(self):
        self.left_motor.run(-self.power)
        self.right_motor.run(self.power)
        return super().left()

    def right(self):
        self.left_motor.run(self.power)
        self.right_motor.run(-self.power)
        return super().right()

    def space(self):
        self.left_motor.brake()
        self.right_motor.brake()
        self.brick.play_tone(440, 500)
        return super().space()

    def stop(self):
        self.left_motor.brake()
        self.right_motor.brake()
        return super().stop()
