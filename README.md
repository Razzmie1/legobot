## Legobot

**Control a LEGO Mindstorms NXT 2.0 robot from a Windows PC or let the AI control it to perform a given task!**

Right now the robot is actually a differential-drive vehicle with left and right road wheels driven by separate motors and can be built using the provided instructions [here](https://www.lego.com/cdn/product-assets/product.bi.core.pdf/4589649.pdf). Forward/backward motion and left/right turns are achieved by commanding these two drive motors with different power values as in tank steering.

This project is intended to get some initial hands on experience in the field of robotic control and vision-language-action (VLA) models and see which difficulties may arise, so everything is kept simple. Furthermore, some parts of the code will be written using Cursor for experimentation and checking to what extent an AI is a useful assistant.

This project’s trajectory:

- **Phase 1 (now)**: Reliably connect to an NXT brick, send motor commands
- **Phase 2**: Teleoperate the vehicle (keyboard/controller) while recording synchronized observations + actions
- **Phase 3**: Train a VLA model to execute tasks from natural-language instructions
- **Phase 4**: Run the trained policy on real hardware with safety constraints and evaluation

## Tech stack (planned)

- **Control & Comms**: Python, [`nxt-python`](https://ni.srht.site/nxt-python/latest/) and PyBluez for NXT 2.0 Bluetooth communication
- **Environment & Tooling**: [`uv`](https://docs.astral.sh/uv/) for virtualenv + dependency management
- **Data & Logging**: Custom Python logging utilities for teleoperation trajectories and episode metadata
- **Vision**: Front-mounted WLAN camera, streamed to the control PC
- **VLA model**: [`OpenVLA`](https://github.com/openvla/openvla) finetuned using PyTorch
- **Clean Code**: [`Ruff`](https://docs.astral.sh/ruff/) for linting and formatting code
- **AI Coding**: [`Cursor`](https://cursor.com/) for experimenting with coding using an AI assistant

## VLA roadmap (planned)

High-level steps:

- Define a simple **action space** for the vehicle
- Define a single **instruction** for simplicity at first
- Build a **robust recorder** that stores data (timestamp, camera image, instruction, action) in a given frequency when teleoperating
- **Collect data** from driving straight lines, turns, stop-on-cue, obstacle avoidance
- **Train** a VLA model that maps `(instruction, image) -> action`, using [`OpenVLA`](https://github.com/openvla/openvla) as the base
- **Evaluate** with clear metrics (success rate, time, collisions, smoothness) and hard safety rules
- **Enhance** the action space and tasks for the robot, for example by using a third motor as forklift
- Train on more data for **several tasks** and evaluate generalization capabilities
