"""
Quick Ollama API check for an image analysis.

Make sure to set the OLLAMA_API_KEY in the .env file and adjust the IMAGE PATH before running this script.
"""

import logging
import os
import time

from dotenv import load_dotenv
from ollama import Client

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(filename)s: %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()

IMAGE_PATH = "data/sample_image.jpg"
OLLAMA_MODEL = "ministral-3:3b-cloud"


def main() -> None:
    system_prompt = "You are an AI assistant that can analyze images and answer questions about them."
    user_prompt = "Describe what you see in this image. Be concise and accurate."
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": user_prompt,
            "images": [IMAGE_PATH],
        },
    ]

    client = Client(
        host="https://ollama.com",
        headers={"Authorization": f"Bearer {os.getenv('OLLAMA_API_KEY')}"},
    )
    logger.info(f"Using image: {IMAGE_PATH}")
    logger.info(f"Using model: {OLLAMA_MODEL}")
    logger.info("Sending request to Ollama...")
    start = time.time()
    response = client.chat(OLLAMA_MODEL, messages=messages, think=False)
    end = time.time()
    logger.info(f"Response Time: {end - start:.2f} seconds")
    logger.info(f"Response Message: {response.message.content}")


if __name__ == "__main__":
    main()
