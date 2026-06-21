import logging

from legobot.apps import GestureControlApp

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(filename)s: %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    app = GestureControlApp(use_brick=False, use_robot_cam=False)
    app.run()


if __name__ == "__main__":
    main()
