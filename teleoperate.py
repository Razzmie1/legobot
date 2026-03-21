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
from typing import Dict, List, Optional, Union

import nxt.locator
from nxt.brick import Brick
from nxt.motor import Motor, Port
from pynput import keyboard

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(filename)s: %(message)s"
)
logger = logging.getLogger(__name__)

PynputKey = Union[keyboard.Key, keyboard.KeyCode]
KeyId = Union[str, keyboard.Key]


# ==========================================
# 1. The Hardware Executor Class
# ==========================================
class NxtRobot:
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


# ==========================================
# 2. The Keyboard Listener Class
# ==========================================
class SteeringController:
    def __init__(self, nxt_robot: NxtRobot) -> None:
        self.action_callback = nxt_robot.execute_command
        self.KEY_MAP: Dict[KeyId, str] = {
            "w": "forward",
            keyboard.Key.up: "forward",
            "s": "backward",
            keyboard.Key.down: "backward",
            "a": "left",
            keyboard.Key.left: "left",
            "d": "right",
            keyboard.Key.right: "right",
            keyboard.Key.space: "space_action",
        }

        self.key_stack: List[KeyId] = []
        self.current_action: Optional[str] = None

        # Trigger the initial paused/stopped state
        self.action_callback(None)

    def update_state(self) -> None:
        new_action: Optional[str] = None

        if self.key_stack:
            top_key: KeyId = self.key_stack[-1]
            new_action = self.KEY_MAP[top_key]

        # ONLY fire the hardware command if the logical action changed
        if new_action != self.current_action:
            self.current_action = new_action
            self.action_callback(self.current_action)

    def get_key_id(self, key: PynputKey) -> Optional[KeyId]:
        if (
            hasattr(key, "char")
            and key.char is not None
            and key.char.lower() in self.KEY_MAP
        ):  # type: ignore
            return key.char.lower()  # type: ignore

        if key in self.KEY_MAP:
            return key  # type: ignore

    def on_press(self, key: PynputKey) -> None:
        key_id: Optional[KeyId] = self.get_key_id(key)
        if key_id is not None:
            # Ignore OS key-repeat spam
            if key_id not in self.key_stack:
                self.key_stack.append(key_id)
                self.update_state()

    def on_release(self, key: PynputKey) -> Optional[bool]:
        if key == keyboard.Key.esc:
            logger.info("Esc pressed. Exiting...")
            return False

        key_id: Optional[KeyId] = self.get_key_id(key)
        if key_id is not None and key_id in self.key_stack:
            self.key_stack.remove(key_id)
            self.update_state()


# ==========================================
# 3. The Main Execution Block
# ==========================================
if __name__ == "__main__":
    logger.info("Attempting to connect to NXT brick via USB/Bluetooth...")

    try:
        with nxt.locator.find() as brick:
            logger.info("Successfully connected to NXT brick!")

            robot = NxtRobot(brick)
            controller = SteeringController(robot)

            logger.info(
                "Engine started. Steer with WASD/Arrows. Press Space for horn. Press ESC to quit."
            )

            with keyboard.Listener(
                on_press=controller.on_press, on_release=controller.on_release
            ) as listener:
                listener.join()

    except nxt.locator.BrickNotFoundError:
        logger.error(
            "ERROR: Could not find the NXT brick. Check your Bluetooth connection."
        )
