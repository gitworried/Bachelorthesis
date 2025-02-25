# sensor_gui/config/settings.py

import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")
SETTINGS_FILE = os.path.join(RESOURCES_DIR, "settings.json")

SAVE_DEFAULT_FOLDER = os.path.join(BASE_DIR, "plots")

THEME_COLORS = {
    "primary_color": "#007054",
    "background_color": "#444444",
    "frame_bg_color": "#222222",
    "text_color": "#FFFFFF",
    "grid_color": "#444444",
    "temperature_color": "#EAA83B",
    "humidity_color": "#315D9A",
    "pressure_color": "#AE2C8A",
    "active_button": "#28BE98",
    "velocity_color": "#3BEA65"
}

GLOBAL_BUTTON_STYLE   = "Custom.TButton"
GLOBAL_TOGGLE_STYLE   = "Custom.TToggle"
GLOBAL_ENTRY_STYLE    = "Custom.TEntry"
GLOBAL_COMBOBOX_STYLE = "Custom.TCombobox"
TOGGLE_BOOTSTYLE      = "success-round-toggle"

HEATER_PIN = 13  # GPIO pin for the heater
FAN_PIN = 12     # GPIO pin for the fan
RESET_PIN = 14   # GPIO pin for the RESET-Function


INVERT_PWM = False
DEFAULT_PWM_FREQUENCY = 5

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
            # Provide fallback if these fields are not present:
            data.setdefault("save_data", False)
            data.setdefault("hostname", "")
            data.setdefault("username", "")
            data.setdefault("password", "")
            data.setdefault("save_directory", SAVE_DEFAULT_FOLDER)
            data.setdefault("save_filename", "sensor_data.md")
            data.setdefault("pwm_frequency", DEFAULT_PWM_FREQUENCY)
            return data
    # default
    return {
        "save_data": False,
        "hostname": "",
        "username": "",
        "password": "",
        "save_directory": SAVE_DEFAULT_FOLDER,
        "save_filename": "sensor_data.md",
        "pwm_frequency": DEFAULT_PWM_FREQUENCY
    }

def save_settings(settings_dict):
    os.makedirs(RESOURCES_DIR, exist_ok=True)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings_dict, f)
