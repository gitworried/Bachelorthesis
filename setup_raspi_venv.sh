# Variables
VENV_DIR="raspi_venv"
PYTHON_VERSION="python3"

# Step 1: Update and install system packages
echo "Updating and installing system packages..."
sudo apt-get update && \
sudo apt-get install -y \
  python3 python3-pip python3-tk python3-numpy python3-matplotlib \
  python3-paramiko python3-pigpio pigpio i2c-tools \
  libqt5waylandclient5 libqt5waylandcompositor5 \
  qtwayland5 xwayland

# Step 2: Install virtualenv
echo "Installing virtualenv..."
sudo pip3 install virtualenv

# Step 3: Create a virtual environment
echo "Creating virtual environment in $VENV_DIR..."
virtualenv -p $PYTHON_VERSION $VENV_DIR

# Step 4: Activate the virtual environment
echo "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Step 5: Install Python modules from PyPI inside the virtual environment
echo "Installing Python modules from PyPI..."
pip install --upgrade pip
pip install \
    adafruit-blinka \
    adafruit-circuitpython-busdevice \
    adafruit-circuitpython-bme280 \
    ttkbootstrap

# Step 6: Force reinstall specific packages (if needed)
echo "Force reinstalling specific packages..."
pip install --upgrade --force-reinstall \
    adafruit-circuitpython-bme280 \
    adafruit-circuitpython-busdevice \
    adafruit-blinka

# Step 7: Deactivate the virtual environment
echo "Deactivating virtual environment..."
deactivate

# Step 8: Reboot the system
echo "Rebooting the system..."
sudo reboot