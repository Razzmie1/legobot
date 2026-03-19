## Legobot

**Control a LEGO Mindstorms NXT 2.0 robot from a Windows PC or let the AI control it to perform a given task!**

Right now the robot is actually a differential-drive vehicle with left and right road wheels driven by separate motors and can be built using the provided instructions [here](https://www.lego.com/cdn/product-assets/product.bi.core.pdf/4589649.pdf). Forward/backward motion and left/right turns are achieved by commanding these two drive motors with different power values as in tank steering.

This project is intended to get some initial hands on experience in the field of robotic control and vision-language-action (VLA) models and see which difficulties may arise, so everything is kept simple. Furthermore, some parts of the code will be written using Cursor for experimentation and checking to what extent an AI is a useful assistant.

This project’s trajectory:

- **Phase 1 (now)**: Reliably connect to an NXT brick, send motor commands
- **Phase 2**: Teleoperate the vehicle (keyboard/controller) while recording synchronized observations + actions
- **Phase 3**: Train a VLA model to execute tasks from natural-language instructions
- **Phase 4**: Run the trained policy on real hardware with safety constraints and evaluation

## Tech Stack (planned)

- **Programming Language**: Python 3.11
- **Communication**: [`NXT-Python`](https://ni.srht.site/nxt-python/latest/) and [`PyBluez`](https://github.com/pybluez/pybluez) for Bluetooth connection to the NXT Brick
- **Remote Control**: [`pynput`](https://github.com/moses-palmer/pynput) for keyboard input handling
- **Environment & Tooling**: [`uv`](https://docs.astral.sh/uv/) for virtualenv + dependency management
- **Data & Logging**: Custom Python logging utilities for teleoperation trajectories and episode metadata
- **Vision**: Front-mounted WLAN camera, streamed to the control PC
- **VLA model**: [`OpenVLA`](https://github.com/openvla/openvla) finetuned using PyTorch
- **Clean Code**: [`Ruff`](https://docs.astral.sh/ruff/) for linting and formatting code
- **AI Coding**: [`Cursor`](https://cursor.com/) for experimenting with coding using an AI assistant

## Teleoperation Roadmap

- Send motor control signals using a python script for testing
- Implement a command translator that maps keyboard input to motor control signals
- Implement a service that listens on keyboard input
- Add a controller as optional input device

## VLA Roadmap (planned)

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
   This creates a virtual environment `.venv` with the required dependencies which should be activated by
   ```powershell
   .venv\Scripts\activate
   ```

## NXT Setup and Bluetooth Tests

### Setup the config file

`nxt-python` can read a configuration file named `.nxt-python.conf`

```ini
[DEFAULT]
backends = bluetooth
host = 00:16:53:0E:40:B1
name = NXT
```

Adjust `host` and `name`, where `host` is the NXT Bluetooth address. The address can be found in the "Settings" menu, under "NXT Version" it is the last line labeled "ID". Add `:` between each pair of digits as shown above.

### Test Bluetooth connection

Run the following script, where a tone from the NXT Brick confirms the Bluetooth connection

```powershell
python test_bluetooth.py
```

Then, run the following script, which sends drive commands to motor ports `A` and `C` (tank steering): drive forward/backward, turn left/right

```powershell
python test_motors.py
```

**Caution:** Make sure the NXT vehicle drives in a safe environment (;

### Troubleshooting

- **NXT Brick not connected properly:** Make sure that you added the NXT Brick as new Bluetooth device and check the Bluetooth settings. In the advanced Bluetooth settings under `COM Ports` there must be an outgoing port for this device. Otherwise there might be an issue with the integrated Bluetooth adapter and its driver, because the NXT Brick is quite old and uses SPP. In my case, buying a cheap Bluetooth Dongle with SPP support solved this issue.