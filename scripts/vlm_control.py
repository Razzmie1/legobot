import logging

from legobot.apps import VLMControlApp

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(filename)s: %(message)s"
)
logger = logging.getLogger(__name__)

USE_BRICK = False


def main():
    app = VLMControlApp(use_brick=False, save_video=False)
    app.run()


if __name__ == "__main__":
    main()
