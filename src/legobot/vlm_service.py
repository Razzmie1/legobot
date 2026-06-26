import base64
import logging
import os
import threading
import time
from typing import Optional

import cv2
from dotenv import load_dotenv
from ollama import ChatResponse, Client

from legobot.cameras import LiveCapture
from legobot.robots import VehicleBase
from legobot.vlm_constants import (
    OLLAMA_MODEL,
    SYSTEM_PROMPT,
    TOOLS,
)

load_dotenv()
logger = logging.getLogger(__name__)


class VLMService:
    """
    Service that captures images, sends them to Ollama VLM and executes actions.
    """

    model = OLLAMA_MODEL
    system_prompt = SYSTEM_PROMPT
    tools = TOOLS

    def __init__(self, user_prompt: str, robot: VehicleBase, live_cap: LiveCapture):
        """
        Initialize the VLMService.

        Args:
            user_prompt: The user prompt that is interpreted by the VLM together with the image to guide the robot's actions.
            robot: The robot instance that will execute actions.
            live_cap: The live capture instance that will provide images.
        """

        self.robot = robot
        self.live_cap = live_cap
        self.client = Client(
            host="https://ollama.com",
            headers={"Authorization": f"Bearer {os.getenv('OLLAMA_API_KEY')}"},
        )
        self.user_prompt = user_prompt
        self.thread = threading.Thread(target=self._worker_loop, daemon=True)

    def call_vlm(self, image_base64: str) -> Optional[ChatResponse]:
        """
        Send request to Ollama VLM with image and prompts.

        Args:
            image_base64: The base64 encoded image from the camera.

        Returns:
            The response from the VLM, or None if there was an error.
        """

        messages = [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "user",
                "content": self.user_prompt,
                "images": [image_base64],
            },
        ]

        try:
            response = self.client.chat(
                self.model, messages, tools=self.tools, think=False
            )
            return response
        except Exception as e:
            logger.error(f"Failed to call VLM: {e}")
            return None

    def execute_action(self, action_name: str) -> None:
        """
        Execute the action on the robot based on the tool call.

        Args:
            action_name: The name of the action to execute, as returned by the VLM tool call.
        """

        action_map = {
            "forward": self.robot.forward,
            "backward": self.robot.backward,
            "left": self.robot.left,
            "right": self.robot.right,
            "stop": self.robot.stop,
            "space": self.robot.space,
        }

        if action_name in action_map:
            action_map[action_name]()
        else:
            logger.warning(f"Unknown action: {action_name}")

    def _worker_loop(self):
        """
        Main loop for processing camera frames and calling the VLM.
        """
        while not self.live_cap.stop_event.is_set():
            frame = self.live_cap.get_frame()
            if frame is None:
                logger.warning("No frame available from camera stream.")
                time.sleep(1)
                continue
            frame = cv2.resize(frame, (640, 480))
            _, buffer = cv2.imencode(".jpg", frame)
            img_base64 = base64.b64encode(buffer).decode("utf-8")

            result = self.call_vlm(img_base64)
            if not result:
                time.sleep(1)
                continue

            logger.info(f"VLMService response: {result.message}")
            tool_calls = result.message.tool_calls
            if tool_calls:
                tool_call = tool_calls[0]
                self.execute_action(tool_call.function.name)
            else:
                logger.info("No tool calls in VLM response.")

            logger.info("Waiting 2 seconds before processing next frame...")
            time.sleep(2)

    def join(self) -> None:
        self.thread.join()

    def start(self) -> None:
        self.live_cap.start()
        self.thread.start()
        logger.info("VLMService started.")

    def stop(self) -> None:
        self.live_cap.stop()
        self.thread.join(timeout=2)
        logger.info("VLMService stopped.")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.stop()
