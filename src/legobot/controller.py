import logging
from typing import Dict, List, Optional, Union
from legobot.nxt_robots import Vehicle
from pynput import keyboard

logger = logging.getLogger(__name__)
PynputKey = Union[keyboard.Key, keyboard.KeyCode]
KeyId = Union[str, keyboard.Key]


class KeyboardController:
    def __init__(self, nxt_robot: Vehicle) -> None:
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
        logger.info(
            "Engine started. Steer with WASD/Arrows. Press Space for horn. Press ESC to quit."
        )

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
            and key.char is not None  # type: ignore
            and key.char.lower() in self.KEY_MAP  # type: ignore
        ):
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
