# Step 1: Update and install system packages
echo "Updating and installing system packages..."
sudo apt-get update && \
sudo apt-get install -y \
  python3 python3-pip python3-tk pigpio

# Step 2: Install Python modules globally
echo "Installing Python modules globally..."
sudo pip3 install --upgrade pip
sudo pip3 install \
    ttkbootstrap \
    paramiko \
    matplotlib \
    numpy

# Step 3: Reboot the system
echo "Rebooting the system..."
sudo reboot