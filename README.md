# Digital Control System for an Eiffel Turbine

## Project Description

This project involves the development of a Graphical User Interface (GUI) for the digital control of a wind tunnel, which serves as a demonstrator at the Berlin University of Applied Sciences (HTW Berlin). The GUI allows interaction with the wind tunnel, including the control of parameters and the reading of sensor data. The goal of the GUI is to create a user-friendly, efficient interface that enables easy operation and analysis of the sensor data.

The following steps explain the system initialization process and provide guidance on how to handle and operate the control unit.

---

## Installation

### 1. Installation on a Raspberry Pi (Local Use)

To use the GUI locally on a Raspberry Pi, the following specific packages need to be installed to support both software and hardware components.

A ready-made script is included in the repository, but it needs to be made executable using the following command first:

```bash
chmod +x setup_raspi_venv.sh
```

Once finished, the script can either be executed using the instruction:

```bash
./setup_raspi_venv.sh
```

or the following steps can be carried out manually.


# Step 1: Update and install system packages
sudo apt-get update && \
sudo apt-get install -y \
  python3 python3-pip python3-tk python3-numpy python3-matplotlib \
  python3-paramiko python3-pigpio pigpio i2c-tools \
  libqt5waylandclient5 libqt5waylandcompositor5 \
  qtwayland5 xwayland

# Step 2: Install virtualenv
sudo pip3 install virtualenv

# Step 3: Create a virtual environment
virtualenv -p $PYTHON_VERSION $VENV_DIR

# Step 4: Activate the virtual environment
source $VENV_DIR/bin/activate

# Step 5: Install Python modules from PyPI inside the virtual environment
pip install --upgrade pip
pip install \
    adafruit-blinka \
    adafruit-circuitpython-busdevice \
    adafruit-circuitpython-bme280 \
    ttkbootstrap

# Step 6: Force reinstall specific packages (if needed)
pip install --upgrade --force-reinstall \
    adafruit-circuitpython-bme280 \
    adafruit-circuitpython-busdevice \
    adafruit-blinka

# Step 7: Deactivate the virtual environment
deactivate

# Step 8: Reboot the system
sudo reboot



### 2. Installation on a Separate Machine (SSH Use)

Similar to the local execution method, additional libraries are required for accessing the system via SSH, which enable the GUI to function remotely. These libraries can also be installed either via the script or manually.

Once again, the script needs to be made executable using the following command:

```bash
chmod +x setup_ubuntu.sh
```

and can be executed using following command:

```bash
./setup_ubuntu.sh
```

Alternatively, the manual installation can be done using the following steps.


# Step 1: Update and install system packages
sudo apt-get update && \
sudo apt-get install -y \
  python3 python3-pip python3-tk pigpio

# Step 2: Install Python modules globally
sudo pip3 install --upgrade pip
sudo pip3 install \
    ttkbootstrap \
    paramiko \
    matplotlib \
    numpy

# Step 3: Reboot the system
sudo reboot

