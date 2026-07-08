OLLAMA_MODEL = "ministral-3:14b-cloud"  # 3b, 8b, 14b

SYSTEM_PROMPT = """
You are the autonomous brain of a small LEGO vehicle. You control the vehicle using an image of a camera.
Analyze the camera image, consider the current task given by the user, and decide on the appropriate action.
Shortly justify your decision in your answer.
"""

VLM_TASK_PROMPT = """
The image shows the front view of the vehicle. The ground is visible in the lower part of the image, and the objects are on top of the ground.
If you see a clear path ahead, move forward or look around by turning left or right.
If you encounter an obstacle in front of you in a really short distance, turn left or right to avoid a collision. 
Note, turning left or right rotates the vehicle in place using tank steering.
Also, the vehicle is quite small and robust, so you can be assertive.
If the image appears to be blurry because of the movement, stop the vehicle to get a clearer view and reassess the situation.
When you see a small ball in front of you, signal a completed task and dont approach it too closely.
Always answer with your analysis and tool choice. That helps me to improve the system and understand your reasoning.
"""

GESTURE_CONTROL_PROMPT = """
Analyze the image and focus only on the hand and extended fingers. Ignore persons and other objects.
Use the perspective of the camera that captured the given frame to determine the direction of the fingers.
Classify the gesture into one of the following categories and call the corresponding tool:
- Finger pointing up: Move forward.
- Finger pointing down: Move backward.
- Finger pointing left: Turn left.
- Finger pointing right: Turn right.
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


TOOLS = [forward, backward, left, right, stop, space]
