import logging
from enum import Enum

from nxt.brick import Brick
from nxt.motor import Port

logger = logging.getLogger(__name__)


class VehicleAction(Enum):
    FORWARD = 1
    BACKWARD = 2
    LEFT = 3
    RIGHT = 4
    SPACE = 5
    STOP = 6


class VehicleBase:
    """
    Base class for vehicles which defines the interface and can be used for testing.
    """

    def __init__(self):
        self.current_action: VehicleAction = VehicleAction.STOP
        self.current_action_count = 0

    def _update_action(self, action: VehicleAction):
        logger.info(f"Executing Action: {action.name}")
        if self.current_action == action:
            self.current_action_count += 1
        else:
            self.current_action = action
            self.current_action_count = 1

    def forward(self):
        self._update_action(VehicleAction.FORWARD)

    def backward(self):
        self._update_action(VehicleAction.BACKWARD)

    def left(self):
        self._update_action(VehicleAction.LEFT)

    def right(self):
        self._update_action(VehicleAction.RIGHT)

    def space(self):
        self._update_action(VehicleAction.SPACE)

    def stop(self):
        self._update_action(VehicleAction.STOP)


class NxtVehicle(VehicleBase):
    """
    A vehicle implementation that controls a physical NXT robot using the nxt-python library.
    """

    def __init__(self, brick: Brick):
        super().__init__()
        self.brick = brick
        self.left_motor = brick.get_motor(Port.C)
        self.right_motor = brick.get_motor(Port.A)

        # Default power level for all movements, should be between 64 and 128
        self.power: int = 100

    def forward(self):
        self.left_motor.run(self.power)
        self.right_motor.run(self.power)
        super().forward()

    def backward(self):
        self.left_motor.run(-self.power)
        self.right_motor.run(-self.power)
        super().backward()

    def left(self):
        self.left_motor.run(-self.power)
        self.right_motor.run(self.power)
        super().left()

    def right(self):
        self.left_motor.run(self.power)
        self.right_motor.run(-self.power)
        super().right()

    def space(self):
        self.left_motor.brake()
        self.right_motor.brake()
        self.brick.play_tone(440, 500)
        super().space()

    def stop(self):
        self.left_motor.brake()
        self.right_motor.brake()
        super().stop()
