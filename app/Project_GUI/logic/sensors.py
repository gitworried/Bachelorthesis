# logic/sensors.py
"""
@file sensors.py
@brief Verwaltung verschiedener Sensoren (Konfiguration, Pfade, Einheiten).
"""

class SensorsManager:
    """
    @class SensorsManager
    @brief Enthält Informationen und Zugriffslogik zu verschiedenen Sensoren,
           z.B. BME280, MCP9600 usw.
    """
    def __init__(self):
        self.andere_sensoren = {
            "BME_Temperature": {
                "name": "BME280 Temperatur",
                "unit": "°C",
                "script_path": "/home/Eiffel/GUI/ssh_control/aggregator.py"
            },
            "BME_Humidity": {
                "name": "BME280 Feuchtigkeit",
                "unit": "%",
                "script_path": "/home/Eiffel/GUI/ssh_control/aggregator.py"
            },
            "BME_Pressure": {
                "name": "BME280 Druck",
                "unit": "hPa",
                "script_path": "/home/Eiffel/GUI/ssh_control/aggregator.py"
            },
            "MCP_Temp": {
                "name": "MCP9600 Temperatur",
                "unit": "°C",
                "script_path": "/home/Eiffel/GUI/ssh_control/aggregator.py"
            },
            "SDP_Pressure": {
                "name": "SDP810 Druck",
                "unit": "Pa",
                "script_path": "/home/Eiffel/GUI/ssh_control/aggregator.py"
            }
        }

    def get_available_other_sensors(self):
        """
        @fn get_available_other_sensors()
        @brief Gibt die Konfiguration aller zusätzlichen Sensoren zurück.
        @return dict
        """
        return self.andere_sensoren
