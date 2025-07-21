# KRAVE Experiment Platform

## Overview

KRAVE is a modular platform for running behavioral neuroscience experiments. It integrates hardware control (cameras, pumps, sensors), experiment logic, data collection, and a user interface for experimenters.

## Features
- **Experiment Control:** Flexible task logic for shaping and regular training sessions.
- **Hardware Integration:** Supports hardware components including visual displays, sounds, cameras, syringe pumps, lick sensors, and ttl pulses sent to other modules.
- **Data Collection:** Automated data writing, metadata management, and file forwarding.
- **User Interface:** Pygame/Tkinter-based UI for experiment setup, monitoring, and data visualization.
- **Configuration:** JSON-based configuration for experiments and cohorts.

## Directory Structure
- `krave/experiment/` — Core experiment logic and hardware testing
- `krave/hardware/` — Hardware interface modules (cameras, spout, sound, visual)
- `krave/helper/` — Utility functions, reward logic, state management
- `krave/output/` — Data writing and transfer
- `krave/ui/` — User interface, buttons, experiment options, data visualization
- `krave/config/` — Experiment and cohort configuration files
- Top-level scripts: `run_task.py`, `calibrate_pump.py`, `free_reward.py`, etc.


## Usage

### 1. Configure Experiment
- Edit or create experiment config files in `krave/config/` as needed.
- Set up hardware configuration in `krave/hardware/hardware.json`.

### 2. Start the User Interface

The main UI allows you to select experiment options, start/stop sessions, and visualize data.

```bash
python -m krave.ui.ui
```

### 3. Run an Experiment Session

The main experiment logic is run via:

```bash
./run_task.sh
```

Or directly:

```bash
python run_task.py
```

### 4. Calibrate Pump

```bash
python calibrate_pump.py
```

### 5. Free Reward

```bash
python free_reward.py
```

## Data Output
- Data and metadata are written to folders specified in `krave/output/data_writer_config.json`.
- Analyzed data and real-time data are available in `krave/ui/analized_data/`.

## Customization
- Add new experiment types by creating new config files in `krave/config/` and updating logic in `krave/experiment/task.py` as needed.
- Hardware modules can be extended in `krave/hardware/`.

## Troubleshooting
- Ensure all hardware is connected and configured as per `hardware.json`.
- For GPIO or camera errors, check permissions and hardware connections.
- Use Python 3.7–3.9 for best compatibility with dependencies.

## Raspberry Pi Setup

To set up KRAVE on a Raspberry Pi (recommended: Raspberry Pi 4 Model B, running Raspberry Pi OS):

### 1. Prerequisites
- Ensure your Pi is running Raspberry Pi OS (legacy version, bullseye 32 bit full).
- Connect all required hardware (cameras, pumps, sensors, etc.).
- Enable the camera interface via `raspi-config` if using PiCamera:
  ```bash
  sudo raspi-config
  # Interfacing Options > Camera > Enable
  sudo reboot
  ```
- Update your system:
  ```bash
  sudo apt-get update && sudo apt-get upgrade
  ```
- Install system dependencies:
  ```bash
  sudo apt-get install python3-pip python3-dev python3-pygame python3-tk python3-pil libatlas-base-dev libopenjp2-7 libtiff5
  ```

### 2. Clone the Repository
```bash
git clone https://github.com/yourusername/krave.git
cd krave
```

### 3. Set Up Python Environment
- (Optional but recommended) Create a virtual environment:
  ```bash
  python3 -m venv KRAVE
  source venv/bin/activate
  ```

### 4. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the UI or Experiment
- Start the UI:
  ```bash
  python -m krave.ui.ui
  ```
- Or run an experiment session:
  ```bash
  ./run_task.sh
  ```

## Contact

For questions or contributions, contact yzhan485@jhmi.edu. 