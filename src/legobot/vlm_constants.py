SYSTEM_PROMPT = """
You are the autonomous brain of a small LEGO vehicle. You control the vehicle using an image of a camera.
Analyze the camera image, consider the current task given by the user, and decide on the appropriate action.
Shortly justify your decision in your answer.
"""

VLM_TASK_PROMPT = """
Navigate through the environment while avoiding obstacles. The task is completed when you see a red ball right in front of you.
"""

GESTURE_CONTROL_PROMPT = """
Analyze the image and focus only on the hand and extended fingers. Ignore faces and other objects.
Classify the image into one of the following categories and call the corresponding tool:
- Pointing up: Move forward.
- Pointing down: Move backward.
- Pointing left: Turn left.
- Pointing right: Turn right.
- Both hands open: Stop.
- Both thumbs up: Task completed.

These categories are only a guideline for you to understand the gestures.
Only if you really can not classify the gesture, you can call the stop tool to be safe, but try to avoid that.
"""


def forward():
    """Move the vehicle forward."""
    pass


def backward():
    """Move the vehicle backward."""
    pass


def left():
    """Turn the vehicle left."""
    pass


def right():
    """Turn the vehicle right."""
    pass


def stop():
    """Stop the vehicle."""
    pass


def space():
    """Play a tone to signal a completed task."""
    pass
