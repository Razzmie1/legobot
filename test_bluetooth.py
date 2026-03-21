"""
NXT-Python tutorial: find the brick.

Please configure the .nxt-python.conf first.
"""

import logging

import nxt.locator

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(filename)s: %(message)s"
)
logger = logging.getLogger(__name__)

with nxt.locator.find() as b:
    logger.info(f"Found brick: {b.get_device_info()[0]}")
    b.play_tone(440, 250)
