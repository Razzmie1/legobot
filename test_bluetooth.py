"""NXT-Python tutorial: find the brick."""
import nxt.locator
import logging
logging.basicConfig(level=logging.DEBUG)

with nxt.locator.find(backends=["bluetooth"], name="NXT", host="00:16:53:0E:40:B1") as b:
    print("Found brick:", b.get_device_info()[0])
    b.play_tone(440, 250)