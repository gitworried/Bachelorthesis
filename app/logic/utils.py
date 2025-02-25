# sensor_gui/logic/utils.py

from config.settings import THEME_COLORS

def get_sensor_color(unit):
    """Return a color for the sensor line based on its unit."""
    if unit == "°C":
        return THEME_COLORS["temperature_color"]
    elif unit == "%":
        return THEME_COLORS["humidity_color"]
    elif unit == "hPa":
        return THEME_COLORS["pressure_color"]
    elif unit == "m/s":
        return THEME_COLORS["velocity_color"]
    else:
        return THEME_COLORS["active_button"]
