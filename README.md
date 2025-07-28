# KRAVE Experiment Platform

## Overview

**KRAVE** is a modular, extensible platform for running neuroscience behavioral experiments. It integrates experiment logic, hardware control, data collection, and an intuitive user interface—designed for fast iteration and stable deployment on Raspberry Pi systems.

---

## Features

- **Flexible Experiment Logic**\
  Easily define shaping and training tasks using a modular state machine framework.

- **Hardware Integration**\
  Supports:

  - Cameras (Basler, PiCamera)
  - Visual and auditory cues
  - TTL pulse delivery
  - Syringe pumps
  - Lick and movement sensors

- **Automated Data Collection**\
  Saves raw and processed data, writes metadata, and supports automatic file transfer to central servers.

- **User Interface**\
  Pygame/Tkinter-based GUI for experiment control, monitoring, and real-time visualization.

- **Configuration System**\
  Experiments and cohorts configured via JSON files for ease of replication and scalability.

---

## Directory Structure

```text
krave/
├── experiment/       # Core experiment logic and task control
├── hardware/         # Interfaces to physical devices (camera, sensors, pumps, etc.)
├── helper/           # Utility functions and state logic
├── output/           # Data writing and syncing
├── ui/               # Graphical user interface and plotting
├── config/           # JSON configuration files
├── run_task.sh       # Launch an experiment session
├── calibrate_pump.py # Run pump calibration
├── free_reward.py    # Deliver a free reward (debugging/training)
```

---

## Usage

### 1. Configure the Experiment

- Edit or create experiment configurations in `krave/config/`
- Edit hardware settings in `krave/hardware/hardware.json`

### 2. Start the UI

```bash
python -m krave.ui.ui
```

### 3. Run an Experiment

```bash
./run_task.sh
```

### 4. Calibrate the Pump

```bash
python calibrate_pump.py
```

### 5. Deliver Free Reward

```bash
python free_reward.py
```

---

## Data Output

- Output data is saved to folders specified in `krave/output/data_writer_config.json`
- Real-time and post-session analysis appears in `krave/ui/analized_data/`

---

## Customization

- To add new task types:\
  Create a new config file in `krave/config/` and extend the logic in `krave/experiment/task.py`

- To add new hardware modules:\
  Add a device interface in `krave/hardware/` and update `hardware.json` accordingly

---

## Raspberry Pi Setup

### Recommended Hardware

- Raspberry Pi 4 Model B (2GB+)
- Raspberry Pi OS Legacy (32-bit, Bullseye preferred)
- Connected hardware (camera, pumps, sensors, etc.)

### 1. System Preparation

```bash
sudo raspi-config
# Enable camera: Interfacing Options > Camera > Enable
sudo reboot

sudo apt update && sudo apt upgrade
sudo apt install python3-pip python3-dev python3-tk python3-pil \
    libatlas-base-dev libopenjp2-7 libtiff5 libjpeg-dev zlib1g-dev libfreetype6-dev \
    libpng-dev libffi-dev libssl-dev build-essential libsdl2-ttf-2.0-0 \
    libsdl2-mixer-2.0-0 libsdl2-image-2.0-0
```

### 2. Clone the Repository

```bash
git clone https://github.com/yourusername/krave.git
cd krave
```

### 3. Set Up Python Environment

```bash
python3 -m venv krave-env
source krave-env/bin/activate
```

### 4. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---
## Troubleshooting

- **🧼 Cleaned Out Broken Environments**\
  If you're experiencing version conflicts or C-extension import errors (e.g. NumPy or pandas):

  ```bash
  rm -rf ~/.local/lib/python3.9/site-packages/*
  ```

  Avoid mixing `sudo pip`, user installs, and venvs.

- **⚙️ Missing SDL or Audio Support (Pygame Fails to Build)**\
  Install development headers for SDL/audio/video before building `pygame`:

  ```bash
  sudo apt install libsdl1.2-dev libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev \
                   libsmpeg-dev libportmidi-dev libavformat-dev libswscale-dev \
                   libjpeg-dev libfreetype6-dev
  ```

- **Missing GPIO**:\
  Run `pip install RPi.GPIO gpiozero`

- **Pandas/NumPy Compatibility**:\
  Use `numpy==1.24.4` and `pandas==2.1.4` for compatibility with Raspberry Pi.

- **Camera Not Detected**:\
  Ensure it's enabled in `raspi-config` and working with `raspistill`.

- **Permissions**:\
  Some hardware (e.g., GPIO or USB cameras) may require root access or udev rules.

- **"Events file not written in time" error**:\
  Indicates the experiment script did not start or failed to create the expected file—check `run_task.sh` and hardware logs.

---

## Contact

Maintainer: Rebekah Zhang\
📧 [yzhan485@jhmi.edu](mailto\:yzhan485@jhmi.edu)

