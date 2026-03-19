"""
NXT-Python tutorial: find the brick.

Please configure the .nxt-python.conf first.
"""

import logging

import nxt.locator

logging.basicConfig(level=logging.DEBUG)

with nxt.locator.find() as b:
    print("Found brick:", b.get_device_info()[0])
    b.play_tone(440, 250)
