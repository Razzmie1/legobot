import logging
from typing import Optional

import nxt.locator
from nxt.brick import Brick

from legobot.cameras import CameraStream
from legobot.robots import NxtVehicle, VehicleBase
from legobot.vlm_service import VLMService

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(filename)s: %(message)s"
)
logger = logging.getLogger(__name__)

USE_BRICK = False


def main():
    brick = initialize_brick()
    robot = NxtVehicle(brick) if brick else VehicleBase()
    camera = CameraStream(0)
    vlm_service = VLMService(robot, camera)

    with vlm_service:
        camera.join()


def initialize_brick() -> Optional[Brick]:
    brick = None
    if USE_BRICK:
        logger.info("Attempting to connect to NXT brick via USB/Bluetooth...")
        try:
            brick = nxt.locator.find()
            logger.info("Connection to NXT brick established successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to NXT brick: {e}")
            logger.info("Continuing in simulation mode without physical brick.")
    else:
        logger.info("Running in simulation mode without physical brick.")
    return brick


if __name__ == "__main__":
    main()
