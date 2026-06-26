import logging
import os
from abc import ABC, abstractmethod
from contextlib import nullcontext
from datetime import datetime
from pathlib import Path
from typing import Optional

import nxt.locator
from dotenv import load_dotenv
from nxt.brick import Brick
from pynput import keyboard

from legobot.cameras import LiveCapture, LiveRender
from legobot.controller import KeyboardController
from legobot.robots import NxtVehicle, VehicleBase
from legobot.vlm_constants import GESTURE_CONTROL_PROMPT, VLM_TASK_PROMPT
from legobot.vlm_service import VLMService

load_dotenv()
logger = logging.getLogger(__name__)


class BaseApp(ABC):
    def __init__(
        self,
        use_brick: bool,
        use_robot_cam: bool,
        use_gesture_cam: bool,
        save_video: bool,
        app_name: str,
    ):
        self.brick = self.init_brick(use_brick)
        self.robot = NxtVehicle(self.brick) if self.brick else VehicleBase()
        self.robot_cap = self.init_cap("ROBOT_CAM_SOURCE") if use_robot_cam else None
        self.gesture_cap = (
            self.init_cap("GESTURE_CAM_SOURCE") if use_gesture_cam else None
        )
        self.save_path = self.create_save_path(app_name) if save_video else None
        self.render = self.init_render()

    @abstractmethod
    def run(self):
        pass

    def init_cap(self, env_source_key: str) -> LiveCapture:
        source = os.getenv(env_source_key)
        if source is None:
            raise KeyError(f"{env_source_key} is not set in the .env file.")
        else:
            if source.isdigit():
                source = int(source)
        logger.info(f"Attempting to initialize camera capture from source: {source}")
        cap = LiveCapture(source)
        logger.info("Camera capture initialized successfully.")
        return cap

    def init_brick(self, use_brick: bool) -> Optional[Brick]:
        brick = None
        if use_brick:
            logger.info("Attempting to connect to NXT brick via USB/Bluetooth...")
            brick = nxt.locator.find()
            logger.info("Connection to NXT brick established successfully.")
        else:
            logger.info("Running in simulation mode without physical brick.")
        return brick

    def init_render(self) -> Optional[LiveRender]:
        render = None
        if self.robot_cap:
            render = LiveRender(
                main_capture=self.robot_cap,
                opt_capture=self.gesture_cap,
                save_path=self.save_path,
                robot=self.robot,
            )
        elif self.gesture_cap:
            render = LiveRender(
                main_capture=self.gesture_cap,
                save_path=self.save_path,
                robot=self.robot,
            )
        logger.info("Render Service initialized successfully.")
        return render

    def create_save_path(self, app_name: str) -> Path:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        return Path(f"data/experiments/{app_name}_{timestamp}.mp4")


class TeleoperateApp(BaseApp):
    def __init__(self, use_brick=False, use_robot_cam=False, save_video=False):
        super().__init__(
            use_brick,
            use_robot_cam,
            use_gesture_cam=False,
            save_video=save_video,
            app_name="teleoperation",
        )
        controller = KeyboardController(self.robot)
        self.listener = keyboard.Listener(
            on_press=controller.on_press,  # type: ignore
            on_release=controller.on_release,  # type: ignore
        )
        logger.info("Keyboard Listener initialized successfully.")

    def run(self):
        with (
            self.brick if self.brick else nullcontext(),
            self.render if self.render else nullcontext(),
            self.listener,
        ):
            self.listener.join()


class GestureControlApp(BaseApp):
    def __init__(self, use_brick=False, use_robot_cam=False, save_video=False):
        super().__init__(
            use_brick,
            use_robot_cam,
            use_gesture_cam=True,
            save_video=save_video,
            app_name="gesture_control",
        )
        assert self.gesture_cap, "gesture_cap must not be None for gesture control"
        self.vlm_service = VLMService(
            GESTURE_CONTROL_PROMPT, self.robot, self.gesture_cap
        )
        logger.info("VLM Service initialized successfully.")

    def run(self):
        assert self.render, "render must not be None to show the gesture cam"
        with self.brick if self.brick else nullcontext(), self.vlm_service, self.render:
            self.render.join()


class VLMControlApp(BaseApp):
    def __init__(self, use_brick=False, save_video=False):
        super().__init__(
            use_brick,
            use_robot_cam=True,
            use_gesture_cam=False,
            save_video=save_video,
            app_name="vlm_control",
        )
        assert self.robot_cap, "robot_cap must not be None for VLM control"
        self.vlm_service = VLMService(VLM_TASK_PROMPT, self.robot, self.robot_cap)
        logger.info("VLM Service initialized successfully.")

    def run(self):
        assert self.render, "render must not be None to show the robot cam"
        with self.brick if self.brick else nullcontext(), self.vlm_service, self.render:
            self.render.join()
