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

from legobot.apps import TeleoperateApp

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(filename)s: %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    app = TeleoperateApp(use_brick=False, use_robot_cam=True, save_video=False)
    app.run()


if __name__ == "__main__":
    main()
