# logic/utils.py
"""
@file utils.py
@brief Hilfsfunktionen und Farbzuweisung für verschiedene Sensoreinheiten.
"""

from config.settings import THEME_COLORS

def get_sensor_color(einheit):
    """
    @fn get_sensor_color(einheit)
    @brief Gibt eine geeignete Farbe für den Sensorplot basierend auf seiner Einheit zurück.
    @param einheit: z.B. "°C", "%", "hPa", ...
    @return Farbwert (Hex)
    """
    if einheit == "°C":
        return THEME_COLORS["temperature_color"]
    elif einheit == "%":
        return THEME_COLORS["humidity_color"]
    elif einheit == "hPa":
        return THEME_COLORS["pressure_color"]
    elif einheit == "m/s":
        return THEME_COLORS["velocity_color"]
    else:
        return THEME_COLORS["active_button"]
