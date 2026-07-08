# Legobot

**Control a LEGO Mindstorms NXT 2.0 robot from a Windows PC or let the AI control it to perform a given task!**

Right now the robot is actually a differential-drive vehicle with left and right road wheels driven by separate motors and can be built using the provided instructions [here](https://www.lego.com/cdn/product-assets/product.bi.core.pdf/4589649.pdf). Forward/backward motion and left/right turns are achieved by commanding these two drive motors with different power values as in tank steering.

This project is intended to get some initial hands on experience in the field of robotic control and vision-language-action (VLA) models and see which difficulties may arise, so everything is kept simple. Furthermore, some parts of the code will be written using Cursor for experimentation and checking to what extent an AI is a useful assistant.

## Tech Stack (planned)

- **Programming Language**: Python 3.11
- **Communication**: [`NXT-Python`](https://ni.srht.site/nxt-python/latest/) and [`PyBluez`](https://github.com/pybluez/pybluez) for Bluetooth connection to the NXT Brick
- **Remote Control**: [`pynput`](https://github.com/moses-palmer/pynput) for keyboard input handling
- **Environment & Tooling**: [`uv`](https://docs.astral.sh/uv/) for virtualenv + dependency management
- **Data & Logging**: Custom Python logging utilities for teleoperation trajectories and episode metadata
- **Vision**: [`OpenCV`](https://opencv.org/) processing images from a local or front-mounted WLAN camera
- **VLM model**: [`Ollama`](https://ollama.com/) cloud model with vision and tool calling capabilities
- **VLA model**: [`OpenVLA`](https://github.com/openvla/openvla) finetuned using PyTorch
- **Clean Code**: [`Ruff`](https://docs.astral.sh/ruff/) for linting and formatting code
- **AI Coding**: [`Cursor`](https://cursor.com/) for experimenting with coding using an AI assistant

## Roadmap

### Teleoperation

- (Optional) Add a controller as input device

### VLM

- Handle case when the VLM is **not responding fast** enough
- **Experiment** with different prompts and also dynamic prompts that e.g. include the action history
- Build a [`Streamlit`](https://streamlit.io/) app to process task prompts from a user and show vehicles view
- Use [`promptfoo`](https://www.promptfoo.dev/) to define a testsuite for prompt engineering

### VLA (planned)

- Define a simple **action space** for the vehicle
- Define a single **instruction** for simplicity at first
- Build a **robust recorder** that stores data (timestamp, camera image, instruction, action) in a given frequency when teleoperating
- **Collect data** from driving straight lines, turns, stop-on-cue, obstacle avoidance
- **Train** a VLA model that maps `(instruction, image) -> action`, using [`OpenVLA`](https://github.com/openvla/openvla) as the base
- **Evaluate** with clear metrics (success rate, time, collisions, smoothness) and hard safety rules
- **Enhance** the action space and tasks for the robot, for example by using a third motor as forklift
- Train on more data for **several tasks** and evaluate generalization capabilities

## Installation

1. This project uses [`uv`](https://docs.astral.sh/uv/) which needs to be installed first
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. Clone this repository
   ```powershell
   git clone https://github.com/Razzmie1/legobot.git your/folder/path
   ```

3. Switch to the repo folder and sync the dependencies of the [`uv.lock`](uv.lock)
   ```powershell
   uv sync
   ```
   This creates a virtual environment `.venv` with the required dependencies which can be activated by
   ```powershell
   .venv\Scripts\activate
   ```

## Setup and Sanity Checks

### Check NXT Bluetooth Connection

`nxt-python` can read a configuration file named `.nxt-python.conf`

```ini
[DEFAULT]
backends = bluetooth
host = 00:16:53:0E:40:B1
name = NXT
```

Adjust `host` and `name`, where `host` is the NXT Bluetooth address. The address can be found in the "Settings" menu, under "NXT Version" it is the last line labeled "ID". Add `:` between each pair of digits as shown above.

Run the following script, where a tone from the NXT Brick confirms the Bluetooth connection

```powershell
uv run scripts\check_bluetooth.py
```

Then, run the following script, which sends drive commands to motor ports `A` and `C` (tank steering): drive forward/backward, turn left/right

```powershell
uv run scripts\check_motors.py
```

**Caution:** Make sure the NXT vehicle drives in a safe environment (;

### Check Camera Connection

Set the `ROBOT_CAM_SOURCE=<your_camera_url>` in the `.env` file and run the following script to check the connection

```powershell
uv run scripts\check_camera.py
```

This should open the camera stream, which you can close by pressing `q`.

### Check Ollama API

Set the `OLLAMA_API_KEY=<your_ollama_api_key>` in the `.env` file and run the following script to check the API

```powershell
uv run scripts\check_ollama.py
```

This should output a short description of this sample [image](data/sample_image.jpg).

### Troubleshooting

- **NXT Brick not connected properly:** Make sure that you added the NXT Brick as new Bluetooth device and check the Bluetooth settings. In the advanced Bluetooth settings under `COM Ports` there must be an `outgoing port` for this device. Otherwise there might be an issue with the integrated Bluetooth adapter and its driver, because the NXT Brick is quite old and uses SPP. In my case, buying a cheap Bluetooth Dongle with SPP support solved this issue.

## Apps

### Teleoperation

Run the teleoperation script

```powershell
uv run scripts\teleoperate.py
```

Use these keyboard controls to drive the vehicle

| Key       | Action       |
|-----------|--------------|
| `W` / `Up`    | Drive forward|
| `S` / `Down`  | Drive backward|
| `A` / `Left`  | Turn left    |
| `D` / `Right` | Turn right   |
| `Space`     | Play tone    |
| `Esc`       | Quit         |

By default, the script runs without a physical NXT brick and without a camera, which can be enabled by setting the corresponding app parameters in the script. Additionally, the video can be saved under [experiments](data/experiments/).

**Caution:** The keyboard **listener stays active** even if you switch windows. Keep the command window or camera stream in focus until you quit with `Esc`. 

**Caution:** Again make sure the NXT vehicle drives in a safe environment

### Gesture Control

Set the `GESTURE_CAM_SOURCE` in the .env file and run the gesture control script

```powershell
uv run scripts\gesture_control.py
```

This will start the camera stream and a VLM will repeatedly analyze the image to execute an appropiate action. The model is guided by the `GESTURE_CONTROL_PROMPT` located [here](src/legobot/vlm_constants.py) and triggers actions via tool calls.

Similar to the teleoperation the following gestures are currently defined

| Gesture   | Action       |
|-----------|--------------|
| `Pointing Up`    | Drive forward|
| `Pointing Down`  | Drive backward|
| `Pointing Left`  | Turn left    |
| `Pointing Right` | Turn right   |
| `Both thumbs up` | Play tone    |
| `Both hands open`| Stop         |

Quit the application by pressing the `Esc` key.

By setting the corresponding app parameters in the script, you can enable the physical NXT brick and an additional robot camera to be shown. For this, you also need to set the `ROBOT_CAM_SOURCE` in the .env file. Additionally, the video can be saved under [experiments](data/experiments/).

**Caution:** The gestures will not always be interpreted correctly and it still can be improved. Feel free to experiment around with different prompts [here](src/legobot/vlm_constants.py) and different models for the [VLMService](src/legobot/vlm_service.py)

### VLM Control

Set the `ROBOT_CAM_SOURCE` in the .env file and run the VLM control script

```powershell
uv run scripts\vlm_control.py
```

This will start the camera stream and a VLM will repeatedly analyze the image to execute an appropiate action. The model is guided by the `VLM_TASK_PROMPT` located [here](src/legobot/vlm_constants.py) and triggers actions via tool calls.

Right now, it simply is ordered to drive around and find a red ball. Feel free to experiment around with different prompts and different models for the [VLMService](src/legobot/vlm_service.py) which might improve performance.

Quit the application by pressing the `Esc` key.

By setting the corresponding app parameters in the script, you can enable the physical NXT brick or save the video under [experiments](data/experiments/).

## Demonstration and Analysis

### The Vehicle

<img width="50%" alt="LegobotVehicle" src="https://github.com/user-attachments/assets/a364c635-cb06-4071-8bd9-dfe3be1b11b8" />

As mentioned above, the vehicle is the basic vehicle provided in the LEGO Mindstorms NXT 2.0 package and a WLAN camera was attached on the front.

### Teleoperation

https://github.com/user-attachments/assets/1b4cd605-558f-4b6b-af64-602d124d2fb9

This is a teleoperation example using the controls as explained above. Teleoperation could be used to collect (image, action) pairs for a given task prompt, which then are part of the train data for e.g. a VLA model. In this example the task could be to explore the environment and find a red ball, where playing a tone signals a finished task.

Compared to the vehicle actions, which are executed almost immediately, the camera stream is transmitted with ~0.5s delay. Thus, the update of the action was artificially delayed by 0.5s to synchronize it and to better convey the idea of teleoperation. In practice, one should use a more advanced (and expensive) camera or even better an embedded system to minimize the latency, because it also affects the runtime performance of an AI model controlling the vehicle.

### Gesture Control

https://github.com/user-attachments/assets/41d98f09-a0dc-40a2-ae83-0a755267f5ab

This is a gesture control example using the prompt described above. In this example an ollama cloud model was used, because the host laptop does not have a suitable GPU. This comes with a latency for the API call and another delay from the model inference. By adjusting the model size one can balance the tradeoff between accuracy and inference time and the general performance can still be improved by prompt engineering or experimenting with different models. Right now, the performance seems to improve when only the gesture is shown without other objects, faces, etc. that introduce noise and also the model seems to struggle when interpreting left and right.

Note that a trained gesture classifier model is probably better suited for this application. Nevertheless, it was implemented out of curiousity as this experiment was achievable simply by adjusting the VLM prompt.

Again, in practice on should use a local model on a inference-optimized GPU to minimize latency when predicting the next action.

### VLM Control

https://github.com/user-attachments/assets/cfe84a9f-799f-493a-b3a6-bf4f5e295b1b

This is a VLM control example using the prompt described above. Just as with the gesture control, there is a delay until the robot reacts to the changing capture of the environment, which makes executing the right action at the right time quite difficult. Another difficulty is the absence of a memory, which means the robot only sees the current image and doesn't know about past images or decisions. The performance can still be improved by prompt engineering or experimenting with different models. Currently, the experiment almost always fails and the episode shown in the video is the best result so far, even though it was conducted in a simple environment.
