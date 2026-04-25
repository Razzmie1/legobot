import logging
from typing import Callable, Dict, List, Optional, Union

from pynput.keyboard import Key, KeyCode

from legobot.cameras import CameraStream
from legobot.robots import VehicleBase

logger = logging.getLogger(__name__)


class KeyboardController:
    def __init__(
        self, vehicle: VehicleBase, camera: Optional[CameraStream] = None
    ) -> None:
        self.pressed_keys: List[Union[Key, KeyCode]] = []
        self.stop_action: Callable = vehicle.stop
        self.current_action: Callable = vehicle.stop
        self.camera = camera
        self.key_to_action: Dict[Union[Key, KeyCode], Callable] = {
            KeyCode.from_char("w"): vehicle.forward,
            KeyCode.from_char("s"): vehicle.backward,
            KeyCode.from_char("a"): vehicle.left,
            KeyCode.from_char("d"): vehicle.right,
            Key.up: vehicle.forward,
            Key.down: vehicle.backward,
            Key.left: vehicle.left,
            Key.right: vehicle.right,
            Key.space: vehicle.space,
        }

        logger.info(
            "Engine started. Steer with WASD/Arrows. Press Space for horn. Press ESC to quit."
        )

    def update_state(self) -> None:
        if self.pressed_keys:
            top_key = self.pressed_keys[-1]
            new_action = self.key_to_action[top_key]
        else:
            new_action = self.stop_action

        if new_action != self.current_action:
            self.current_action = new_action
            self.current_action()

    def on_press(self, key: Union[Key, KeyCode]) -> None:
        if key in self.key_to_action:
            # Ignore OS key-repeat spam
            if key not in self.pressed_keys:
                self.pressed_keys.append(key)
                self.update_state()

    def on_release(self, key: Union[Key, KeyCode]) -> Optional[bool]:
        if key == Key.esc:
            if self.camera:
                self.camera.stop_event.set()
            self.stop_action()
            logger.info("Esc pressed. Exiting...")
            return False

        if key in self.key_to_action:
            if key in self.pressed_keys:
                self.pressed_keys.remove(key)
                self.update_state()
